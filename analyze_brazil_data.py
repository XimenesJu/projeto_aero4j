import pandas as pd

print("Analisando dados do Brasil...")
print("=" * 60)

# Aeroportos
print("\n1. AEROPORTOS BRASILEIROS:")
airports_df = pd.read_csv('https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv')
br_airports = airports_df[airports_df['iso_country'] == 'BR'].copy()
br_airports_iata = br_airports[br_airports['iata_code'].notna()].copy()
print(f"   Total de aeroportos BR com código IATA: {len(br_airports_iata)}")

# Rotas
print("\n2. ROTAS:")
routes_df = pd.read_csv('https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/13e519574832172b538fd5588673132cb826cd20/routes.csv')
print(f"   Total de rotas no CSV: {len(routes_df)}")

# Códigos brasileiros
br_codes = set(br_airports_iata['iata_code'].str.strip().str.upper().values)
print(f"   Códigos IATA brasileiros: {len(br_codes)}")

# Rotas domésticas (origem E destino no Brasil)
domestic_routes = routes_df[
    (routes_df['source_airport'].isin(br_codes)) & 
    (routes_df['destination_apirport'].isin(br_codes))
].copy()
print(f"   Rotas domésticas (BR → BR): {len(domestic_routes)}")

# Rotas internacionais (pelo menos uma ponta no Brasil)
international_routes = routes_df[
    ((routes_df['source_airport'].isin(br_codes)) | 
     (routes_df['destination_apirport'].isin(br_codes))) &
    ~((routes_df['source_airport'].isin(br_codes)) & 
      (routes_df['destination_apirport'].isin(br_codes)))
].copy()
print(f"   Rotas internacionais (BR ↔ Mundo): {len(international_routes)}")

# Aeroportos com rotas domésticas
airports_in_domestic = set(domestic_routes['source_airport'].unique()) | set(domestic_routes['destination_apirport'].unique())
print(f"   Aeroportos BR com rotas domésticas: {len(airports_in_domestic)}")

# Airlines
print("\n3. COMPANHIAS AÉREAS:")
unique_airlines_domestic = domestic_routes['airline'].dropna().unique()
unique_airlines_domestic = [a for a in unique_airlines_domestic if str(a).lower() not in ['unknown', '', 'null', 'none']]
print(f"   Airlines operando rotas domésticas: {len(unique_airlines_domestic)}")
print(f"   Exemplos: {sorted(unique_airlines_domestic)[:10]}")

print("\n" + "=" * 60)
print("RESUMO PARA O DATASET BRASIL:")
print(f"   - Aeroportos (com rotas domésticas): {len(airports_in_domestic)}")
print(f"   - Companhias aéreas: {len(unique_airlines_domestic)}")
print(f"   - Rotas domésticas: {len(domestic_routes)}")
print("=" * 60)
