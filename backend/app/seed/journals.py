"""UTD24 期刊种子数据"""
from sqlalchemy import select
from app.database import async_session_factory, engine
from app.models.journal import Journal

UTD24_JOURNALS = [
    {"name":"The Accounting Review","abbreviation":"AR","publisher":"AAA","issn":"0001-4826","platform":"aaahq","utd24_index":1},
    {"name":"Journal of Accounting and Economics","abbreviation":"JAE","publisher":"Elsevier","issn":"0165-4101","platform":"elsevier","utd24_index":2},
    {"name":"Journal of Accounting Research","abbreviation":"JAR","publisher":"Wiley","issn":"0021-8456","platform":"wiley","utd24_index":3},
    {"name":"Journal of Finance","abbreviation":"JF","publisher":"Wiley","issn":"0022-1082","platform":"wiley","utd24_index":4},
    {"name":"Journal of Financial Economics","abbreviation":"JFE","publisher":"Elsevier","issn":"0304-405X","platform":"elsevier","utd24_index":5},
    {"name":"The Review of Financial Studies","abbreviation":"RFS","publisher":"Oxford","issn":"0893-9454","platform":"oxford","utd24_index":6},
    {"name":"Information Systems Research","abbreviation":"ISR","publisher":"INFORMS","issn":"1047-7047","platform":"informs","utd24_index":7},
    {"name":"INFORMS Journal on Computing","abbreviation":"JOC","publisher":"INFORMS","issn":"1091-9856","platform":"informs","utd24_index":8},
    {"name":"MIS Quarterly","abbreviation":"MISQ","publisher":"U of Minnesota","issn":"0276-7783","platform":"misq","utd24_index":9},
    {"name":"Journal of Consumer Research","abbreviation":"JCR","publisher":"Oxford","issn":"0093-5301","platform":"oxford","utd24_index":10},
    {"name":"Journal of Marketing","abbreviation":"JM","publisher":"AMA/SAGE","issn":"0022-2429","platform":"sage","utd24_index":11},
    {"name":"Journal of Marketing Research","abbreviation":"JMR","publisher":"AMA/SAGE","issn":"0022-2437","platform":"sage","utd24_index":12},
    {"name":"Marketing Science","abbreviation":"MKS","publisher":"INFORMS","issn":"0732-2399","platform":"informs","utd24_index":13},
    {"name":"Management Science","abbreviation":"MS","publisher":"INFORMS","issn":"0025-1909","platform":"informs","utd24_index":14},
    {"name":"Operations Research","abbreviation":"OR","publisher":"INFORMS","issn":"0030-364X","platform":"informs","utd24_index":15},
    {"name":"Journal of Operations Management","abbreviation":"JOM","publisher":"Wiley","issn":"0272-6963","platform":"wiley","utd24_index":16},
    {"name":"M&SOM","abbreviation":"M&SOM","publisher":"INFORMS","issn":"1523-4614","platform":"informs","utd24_index":17},
    {"name":"Production and Operations Management","abbreviation":"POM","publisher":"SAGE","issn":"1059-1478","platform":"sage","utd24_index":18},
    {"name":"Academy of Management Journal","abbreviation":"AMJ","publisher":"AOM","issn":"0001-4273","platform":"aom","utd24_index":19},
    {"name":"Academy of Management Review","abbreviation":"AMR","publisher":"AOM","issn":"0363-7425","platform":"aom","utd24_index":20},
    {"name":"Administrative Science Quarterly","abbreviation":"ASQ","publisher":"SAGE","issn":"0001-8392","platform":"sage","utd24_index":21},
    {"name":"Organization Science","abbreviation":"OS","publisher":"INFORMS","issn":"1047-7039","platform":"informs","utd24_index":22},
    {"name":"JIBS","abbreviation":"JIBS","publisher":"Springer","issn":"0047-2506","platform":"springer","utd24_index":23},
    {"name":"Strategic Management Journal","abbreviation":"SMJ","publisher":"Wiley","issn":"0143-2095","platform":"wiley","utd24_index":24},
]

async def seed_journals_sync():
    """种子数据"""
    async with async_session_factory() as db:
        for j_data in UTD24_JOURNALS:
            result = await db.execute(select(Journal).where(Journal.issn == j_data["issn"]))
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in j_data.items():
                    setattr(existing, key, value)
            else:
                db.add(Journal(**j_data))
        await db.commit()
        print(f"Seeded {len(UTD24_JOURNALS)} UTD24 journals")
