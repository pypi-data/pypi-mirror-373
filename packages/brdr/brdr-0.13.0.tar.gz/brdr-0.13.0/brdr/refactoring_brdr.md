# Loaders

## Load_thematic_data 

OK, injects loader en dicts van eigenschappen
vraag: interface van properties dict?

# Load_reference_data
OK -> injects
vraag: interface van properties dict?

## processors

# process_geometry

- publiek
- herwerken met injectie van GeomProcessor? Momenteel switched de code op basis van 
  de types van inputgeometrieën tussen brdr/diessaert. Dit zou in de toelomst misschien ook kunnen per input feature (dus als alle overlappende features uit de reference layer (multi-) polygonen zijn.
- Open Domain (is dit de juiste term?). Openbaar domein is in de context zoals wij deze kennen
  niet-bestaand in veel landen. Ook lijkt dit nogal gebonden aan het ide evan percelen en openbare
  ruimte als thematische en/of referentielagen. (void area, empty area, ???)
- kijken of er niet meer kan onderverdeeld worden in functies die makkelijer te unit testen zijn (bvb de all_polygons check)


# _process_geometry_by_snap

- herwerken naar proces_geometry supplied by a GeomProcessor (cfr. loaders?)

# _process_geometry_by_brdr

- herwerken naar proces_geometry supplied by a GeomProcessor (cfr. loaders?)

# process

- is relevant_distance parameter nog relevant? We hebben hem, maar enkel om om te zetten naar een 
lijst via `relevant_distances = [relevant_distance]`. Mij lijkt het dat we dit kunnen vervangen door in plaats van None te geven als default voor relevant_distances, we default `[1]` zetten
