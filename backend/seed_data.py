"""
Seed database with landmark cases data
Run this script once to populate the database with landmark cases
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Landmark cases data
landmark_cases = [
    {
        "caseNumber": "SC2020-MONASKY",
        "year": 2020,
        "countries": {
            "de": "USA - Italien",
            "en": "USA - Italy"
        },
        "title": {
            "de": "Monasky v. Taglieri (2020) - U.S. Supreme Court",
            "en": "Monasky v. Taglieri (2020) - U.S. Supreme Court"
        },
        "description": {
            "de": "Wegweisender Fall des U.S. Supreme Court zur Bestimmung des 'gewöhnlichen Aufenthalts' eines Kindes. Das Gericht entschied, dass der gewöhnliche Aufenthalt anhand der Gesamtheit der Umstände bestimmt wird, nicht nur aufgrund der elterlichen Absicht.",
            "en": "Landmark U.S. Supreme Court case clarifying determination of a child's 'habitual residence.' The Court held that habitual residence is determined by the totality of circumstances, not by parental intent alone."
        },
        "outcome": {
            "de": "Erfolgreich",
            "en": "Successful"
        },
        "facts": {
            "de": "Amerikanische Mutter und italienischer Vater lebten in Italien. Nach Beziehungsende kehrte die Mutter mit dem Säugling in die USA zurück. Vater beantragte Rückführung nach Italien gemäß Haager Übereinkommen.",
            "en": "American mother and Italian father lived together in Italy. After relationship deteriorated, mother returned to U.S. with infant. Father filed Hague Convention petition seeking child's return to Italy."
        },
        "legalPrinciple": {
            "de": "Der gewöhnliche Aufenthalt wird durch die Gesamtheit der Umstände bestimmt, einschließlich der tatsächlichen Lebensumstände, der Verbindungen des Kindes zum Land und der Dauer des Aufenthalts.",
            "en": "Habitual residence is determined by totality of circumstances, including actual living arrangements, child's connections to the country, and duration of stay."
        },
        "impact": {
            "de": "Führender Präzedenzfall in US-Gerichten zur Bestimmung des gewöhnlichen Aufenthalts. Erleichtert zurückgebliebenen Eltern die Rückführung ihrer Kinder.",
            "en": "Leading precedent in U.S. courts for determining habitual residence. Makes it easier for left-behind parents to seek return of children."
        }
    },
    {
        "caseNumber": "SC2023-WINSTON",
        "year": 2023,
        "countries": {
            "de": "USA - Mexiko",
            "en": "USA - Mexico"
        },
        "title": {
            "de": "Winston & Strawn - Mexiko Rückführungsfall (2023)",
            "en": "Winston & Strawn - Mexico Return Case (2023)"
        },
        "description": {
            "de": "Präzedenzfall zur Rückführung eines aus Mexiko in die USA entführten Kindes. Das Gericht wies die 'gut integriert'-Verteidigung der Mutter zurück und ordnete die Rückführung an.",
            "en": "Precedent-setting case for return of child abducted from Mexico to U.S. Court rejected mother's 'well-settled' defense and ordered child's return."
        },
        "outcome": {
            "de": "Erfolgreich",
            "en": "Successful"
        },
        "facts": {
            "de": "Kind war gewöhnlich in Mexiko ansässig, wo Eltern gemeinsames Sorgerecht hatten. Mutter behielt Kind nach Besuch unrechtmäßig in den USA und beantragte Asyl.",
            "en": "Child was habitually resident in Mexico where parents shared custody. Mother wrongfully retained child in U.S. after visit and claimed asylum."
        },
        "legalPrinciple": {
            "de": "Die Verbindungen des Kindes zum Land des gewöhnlichen Aufenthalts (Familie, Schule, Gemeinschaft) überwiegen die kurze Zeit in einem neuen Land bei der Beurteilung der Integration.",
            "en": "Child's connections to country of habitual residence (family, school, community) outweigh short time in new country when evaluating 'well-settled' defense."
        },
        "impact": {
            "de": "Erschwert entführenden Eltern die Vermeidung der Rückführung durch kurzfristige Integration. Betont die Wichtigkeit schnellen Handelns.",
            "en": "Makes it harder for abducting parents to avoid return based on short-term integration. Emphasizes importance of prompt action."
        }
    },
    {
        "caseNumber": "SC2021-URGENT",
        "year": 2021,
        "countries": {
            "de": "Deutschland - Niederlande",
            "en": "Germany - Netherlands"
        },
        "title": {
            "de": "Dringende Schutzmaßnahmen - Deutschland/Niederlande (2021)",
            "en": "Emergency Protection Measures - Germany/Netherlands (2021)"
        },
        "description": {
            "de": "Fall demonstriert erfolgreiche Koordination zwischen deutschen und niederländischen Behörden zur Sicherstellung der Kinderrückführung innerhalb von 6 Wochen.",
            "en": "Case demonstrates successful coordination between German and Dutch authorities to secure child's return within 6 weeks."
        },
        "outcome": {
            "de": "Erfolgreich",
            "en": "Successful"
        },
        "facts": {
            "de": "Deutscher Vater suchte Rückführung seiner 4-jährigen Tochter aus den Niederlanden. Mutter hatte das Kind nach einem vereinbarten Besuch nicht zurückgebracht.",
            "en": "German father sought return of 4-year-old daughter from Netherlands. Mother failed to return child after agreed visit."
        },
        "legalPrinciple": {
            "de": "Schnelle gerichtliche Entscheidungen und internationale Zusammenarbeit sind entscheidend für erfolgreiche Rückführungen gemäß Haager Übereinkommen.",
            "en": "Swift court decisions and international cooperation are critical for successful returns under Hague Convention."
        },
        "impact": {
            "de": "Zeigt die Effektivität der EU-weiten Zusammenarbeit bei Kindesentführungsfällen und die Bedeutung forensischer Beweise.",
            "en": "Shows effectiveness of EU-wide cooperation in child abduction cases and importance of forensic evidence."
        }
    }
]

async def seed_database():
    """Seed the database with landmark cases"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'safechild')]
    
    try:
        # Clear existing landmark cases
        await db.landmark_cases.delete_many({})
        print("Cleared existing landmark cases")
        
        # Insert new landmark cases
        result = await db.landmark_cases.insert_many(landmark_cases)
        print(f"Inserted {len(result.inserted_ids)} landmark cases")
        
        # Verify insertion
        count = await db.landmark_cases.count_documents({})
        print(f"Total landmark cases in database: {count}")
        
        # Create indexes
        await db.landmark_cases.create_index("caseNumber", unique=True)
        await db.clients.create_index("clientNumber", unique=True)
        await db.documents.create_index("documentNumber", unique=True)
        print("Created database indexes")
        
        print("\n✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
