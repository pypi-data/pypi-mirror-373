




SCHEMA_ID = "http://glowinthedark.co.uk/test/jackrussell/20191009-150413-911278/schema#"


def mutate(db, doc):

    colour = doc.colour
    if colour is None:
        doc.colour = "red"

    doc.schema = SCHEMA_ID
    doc.save(db)


