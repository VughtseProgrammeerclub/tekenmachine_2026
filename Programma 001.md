# Van hoeken naar xy coördinaten
Met de twee servo's kunnen we de pen naar ieder punt op het papier laten bewegen. Dit gaat echter in gebogen lijnen en ik wil uiteindelijk een rechte lijn kunnen tekenen. Hier komt wat goniometrie bij kijken.
Meetkundig ziet de situatie er zo uit:
<img src="goniometrie.png" alt="VPC tekening" width="500">

* De schouderservo bevindt zich op punt (0,0) en heeft een draaibereik van 180° **rechtsom**
* De elleboogservo zit tussen de bovenarm (8 cm) en de onderarm (6cm) en heeft ook een draaibereik van 180°. Omdat deze servo op de kop is gemonteerd is de draairichting **linksom**
* De pen staat op het coördinaat (x,y)

## Uitdaging
De uitdaging is nu om een algoritme te bedenken waarmee bij een xy-coördinaat de hoek van de schouderservo **∠S** en van de elleboogservo **∠E** te bepalen.

Als eerste hebben we hiervoor de afstand **L** van de pen (x,y) tot de schouderservo (0,0) nodig. Dit kan met de stelling van Pythagoras:
<img src="formule_pythagoras.png" alt="Stelling van Pythagoras" width="500">

In Python ziet dat er zo uit:

```python
import math

L = math.sqrt(x**2 + y**2)
```

Nu we **L** weten kunnen we alle hoeken bepalen. Dit gaat met de **cosinusformule**:
