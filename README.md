# Cattler Feedyards

## Decisiones técnicas y supuestos
- No se solicita nombre de lote para la creación del mismo, sino que directamente se lo nombra "Lote <<fecha>>", por ejemplo "Lote 10-06-2026"
- Los animales no tienen identidad externa, son N instancias homogéneas
- La lógica de la creación del lote se separó en un servicio aparte, dado que es una función compleja que incluye creaciones en más de un modelo
- Pensé bien en qué parte usar este servicio, y decidí hacerlo en el serializador, sobreescribiendo el `create`, que es el último paso (dentro del `serializer.save`). Este es el punto donde vi más adecuado trabajarlo por tratarse de datos ya validados.
- Uso de la anotación `@transaction.atomic` para garantizar la atomicidad de los datos creados. Si bulk_create falla por alguna razón, no deberían quedar lotes incompletos o sin todos sus registros de peso.

## Trade-offs
- En la lógica de creación del lote, se priorizó minimizar la cantidad de queries y no la optimización de memoria. Por ejemplo, si se cargan 400 animales y la fecha de ingreso es hace 1 año, serán 400 * 365 = 146000 objetos de Python en memoria antes del bulk_create. Si bien se usó el parámetro batch_size para la creación, para disminuir el impacto sobre la base de datos, el impacto sobre la memoria sigue estando. Se podría usar la misma estrategia para la memoria: un condicional en el bucle que cada 5000 iteraciones (mismo batch_size que en bulk_create) envíe las instancias a la db y limpie la lista en memoria. El bucle continúa, arma el siguiente batch en memoria, lo manda a la db, y así sucesivamente.