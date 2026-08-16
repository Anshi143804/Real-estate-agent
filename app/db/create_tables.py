from app.db.database import Base, engine
import app.db.models

print("=" * 50)
print("Engine:", engine)
print("Database URL:", engine.url)
print()

print("Registered tables:")
print(list(Base.metadata.tables.keys()))
print("=" * 50)

Base.metadata.create_all(bind=engine)

print("Finished creating tables.")