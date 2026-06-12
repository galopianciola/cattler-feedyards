# Cattler Feedyards

## Correr el proyecto
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
pytest  # tests
python manage.py runserver
```

## Colección Bruno
En `requests-collection/` hay requests para happy path y validaciones.

## Superuser (para usar admin)
`User` extiende `AbstractUser` y tiene un `feedyard` obligatorio (ForeignKey, sin null).
`createsuperuser` no pide feedyard por defecto, así que el comando interactivo falla por el not null constraint.

Desde el shell
```bash
feedyard = Feedyard.objects.first()
User.objects.create_superuser(
    username="admin",
    password="admin",
    feedyard=feedyard,
    language="es",
)
```

## Decisiones técnicas y supuestos
- No se solicita nombre de lote para la creación del mismo, sino que directamente se lo nombra "Lote <<fecha>>", por ejemplo "Lote 10-06-2026"
- Los animales no tienen identidad externa, son N instancias homogéneas
- La lógica de la creación del lote se separó en un servicio aparte, dado que es una función compleja que incluye creaciones en más de un modelo
- Pensé bien en qué parte usar este servicio, y decidí hacerlo en el serializador, sobreescribiendo el `create`, que es el último paso (dentro del `serializer.save`). Este es el punto donde vi más adecuado trabajarlo por tratarse de datos ya validados.
- Uso de la anotación `@transaction.atomic` para garantizar la atomicidad de los datos creados. Si bulk_create falla por alguna razón, no deberían quedar lotes incompletos o sin todos sus registros de peso.
- Django rest siempre lanza los errores de campo en serializer como 400. Se pide 409, así que hice una excepcion custom ConflictValidationError con ese status y un mixin que sobreescribe is_valid y vuelve a levantar esa excepción con `self.errors`. Las validaciones quedan en el serializer (como validate_...) y el status HTTP queda en el mixin.
- En el endpoint de actualización de peso del lote, al validar que la fecha especificada no es futura, asumo que las fechas en que ingresaron los animales son todas iguales dentro del lote (como lo establece el endpoint de creación)

## Trade-offs
- En la lógica de creación del lote, se priorizó minimizar la cantidad de queries y no la optimización de memoria. Por ejemplo, si se cargan 400 animales y la fecha de ingreso es hace 1 año, serán 400 * 365 = 146000 objetos de Python en memoria antes del bulk_create. Si bien se usó el parámetro batch_size para la creación, para disminuir el impacto sobre la base de datos, el impacto sobre la memoria sigue estando. Se podría usar la misma estrategia para la memoria: un condicional en el bucle que cada 5000 iteraciones (mismo batch_size que en bulk_create) envíe las instancias a la db y limpie la lista en memoria. El bucle continúa, arma el siguiente batch en memoria, lo manda a la db, y así sucesivamente.
- DRF autentica por token en la vista (TokenAuthentication por defecto con el permiso IsAuthenticated). El middleware de idioma corre antes y necesita User.language. Resolví el token en el middleware para activar la traducción antes del serializer. La alternativa sería una clase de autenticación custom que también active idioma, pero acá se requería middleware.