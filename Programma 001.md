# Van hoeken naar xy-coördinaten
Met de twee servo's kunnen we de pen naar ieder punt op het papier laten bewegen. Dit gaat echter in gebogen lijnen en ik wil uiteindelijk een rechte lijn kunnen tekenen. Hier komt wat goniometrie bij kijken.
Meetkundig ziet de situatie er zo uit:

<img src="gonio.png" alt="VPC tekening" width="500">

* De schouderservo bevindt zich op punt (0,0) en heeft een draaibereik van 180° **rechtsom**
* De elleboogservo zit tussen de bovenarm (8 cm) en de onderarm (6cm) en heeft ook een draaibereik van 180°. Omdat deze servo op de kop is gemonteerd is de draairichting **linksom**
* De pen staat op het coördinaat (x,y)

## Uitdaging
De uitdaging is nu om een algoritme te bedenken waarmee bij een xy-coördinaat de hoek van de schouderservo **∠S** en van de elleboogservo **∠E** te bepalen.

Als eerste hebben we hiervoor de afstand **L** van de pen (x,y) tot de schouderservo (0,0) nodig. Dit kan met de **stelling van Pythagoras**:
<img src="formule_pythagoras.png" alt="Stelling van Pythagoras" width="300">

In Python ziet dat er zo uit:

```python
import math

L = math.sqrt(x**2 + y**2)
```

Nu we **L** weten kunnen we alle hoeken bepalen. Dit gaat met de **cosinusregel**:
<img src="formule_cosinusformule.png" alt="Cosinusregel" width="500">

Met deze regel kan je iedere hoek in een driehoek bepalen als de lengtes van de drie zijden bekend zijn.
Hierboven is C de hoek die tegenover zijde c ligt.
In Python doe je dit zo:

```python
import math

a = 8
b = 8
c = 10

waarde = (a**2 + b**2 - c**2) / (2 * a * b)

hoek = math.acos(waarde)
hoek_graden = math.degrees(hoek)

print(hoek_graden)
```

Op het einde van de code worden de *hoek* (radialen) omgezet naar *hoek_graden*. 360 graden komen overeen met 2π (~6,26) radialen.

## Hoek elleboog
Als we kijken naar de elleboogservo dan zien we dat de hoek **∠E** zich in een driehoek bevindt van de bovenarm (8 cm) , onderarm (6 cm) en L. In formule vorm ziet dit er zo uit:

<img src="formule_cosinusregel2.png" alt="Cosinusregel" width="500">

Als we de lengtes van de armen invullen en op de plaats van **L** de eerdere stelling van Pythagoras zetten, blijft dit over:

<img src="formule_hoek_E.png" alt="Formule voor hoek E" width="500">

```Python
import math

hoek_E = math.degrees(
    math.acos((100 - x**2 - y**2) / 96)
)
```
## Hoek schouder
Voor het berekenen van de hoek van de schouderservo moeten we iets meer stappen maken, maar veel meer dan (twee keer) de cosinusregel hebben we niet nodig. Hier een detail van de tekening van het het draaipunt rond de schouderservo.

<img src="gonio_detail.png" alt="Detail schouder" width="700">

De hoek van de schouder **∠S** is 180° min (hoek **∠a** + **∠b**)

De hoeken **∠a** en **∠b** kunnen we allebei berekenen met de cosinusregel:


### Cosinusregel voor ∠a

<img src="formule_hoek_a_1.png" alt="Formule voor hoek a" width="400">

Hierin vervangen we L door de eerdere stelling van Pythagoras:

<img src="formule_hoek_a_2.png" alt="Formule voor hoek a gesubstitueerd" width="400">

Als we nu de bekende lengtes van de armen invullen dan houden we dit over:

<img src="formule_hoek_a_3.png" alt="Formule voor hoek a ingevuld" width="300">

In Python ziet het er zo uit:

```Python
import math
L = math.sqrt(x**2 + y**2)
waarde = (x**2 + y**2 + 28) / (16 * L)
hoek_a = math.degrees(math.acos(waarde))
print(hoek_a)
```
### Cosinusregel voor ∠b

<img src="formule_hoek_b_1.png" alt="Formule voor hoek b" height="100">
Als we hierin Pythagoras invullen dan kan er veel worden weggestreept en blijft dit over:

<img src="formule_hoek_b_2.png" alt="Formule voor hoek b met Pythagoras" height="100">

Dit is de hoek met de X-as

In Python gaat dit zo:
```Python
import math
hoek_b = math.degrees(
    math.acos(x / math.sqrt(x**2 + y**2))
)
```
### Berekening ∠S
De hoek van de schouder **∠S** is 180° min (hoek **∠a** + **∠b**)
<img src="formule_hoek_s.png" alt="Formule voor hoek S" height="200">

De code voor het bepalen van de hoek van de schouderservo is dan:

```Python
import math

# lengte van lijn naar doelpunt
L = math.sqrt(x**2 + y**2)

# hoek a
hoek_a = math.degrees(
    math.acos(
        (x**2 + y**2 + 28)
        / (16 * L)
    )
)

# hoek b
hoek_b = math.degrees(
    math.acos(x / L)
)

# schouderhoek
hoek_S = 180 - hoek_a - hoek_b

print(hoek_S)
```
