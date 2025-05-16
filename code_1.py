import pandas as pd

# === 1. Load Emissions Dataset ===
emissions = pd.read_csv("co-emissions-by-sector.csv")
emissions.columns = emissions.columns.str.strip().str.lower().str.replace(' ', '_')

# Optional: Recalculate total emissions
sector_cols = [
    'carbon_dioxide_emissions_from_buildings',
    'carbon_dioxide_emissions_from_industry',
    'carbon_dioxide_emissions_from_land_use_change_and_forestry',
    'carbon_dioxide_emissions_from_other_fuel_combustion',
    'carbon_dioxide_emissions_from_transport',
    'carbon_dioxide_emissions_from_manufacturing_and_construction',
    'fugitive_emissions_of_carbon_dioxide_from_energy_production',
    'carbon_dioxide_emissions_from_electricity_and_heat',
    'carbon_dioxide_emissions_from_bunker_fuels'
]
emissions[sector_cols] = emissions[sector_cols].apply(pd.to_numeric, errors='coerce')
emissions['total_emissions'] = emissions[sector_cols].sum(axis=1)

# === 2. Load and Reshape Population Dataset ===
population = pd.read_csv("population.csv")
population = population.rename(columns={'Country/Territory': 'entity'})

# Identify all population year columns (e.g., '2022 Population', '2020 Population', ...)
pop_cols = [col for col in population.columns if 'Population' in col and col[:4].isdigit()]
pop_melted = population.melt(
    id_vars=['entity'],
    value_vars=pop_cols,
    var_name='year',
    value_name='population'
)
# Extract year from column names
pop_melted['year'] = pop_melted['year'].str.extract(r'(\d{4})').astype(int)
pop_melted['population'] = pd.to_numeric(pop_melted['population'], errors='coerce')

# === 3. Load and Reshape GDP Dataset ===
gdp = pd.read_csv("gdp.csv")
gdp = gdp.rename(columns={'Country Name': 'entity'})

# Melt GDP years (1960–2020) to long format
year_cols = [col for col in gdp.columns if col.isdigit()]
gdp_melted = gdp.melt(
    id_vars=['entity'],
    value_vars=year_cols,
    var_name='year',
    value_name='gdp'
)
gdp_melted['year'] = gdp_melted['year'].astype(int)
gdp_melted['gdp'] = pd.to_numeric(gdp_melted['gdp'], errors='coerce')

# === 4. Merge Datasets on Entity + Year ===
df = emissions.merge(pop_melted, on=['entity', 'year'], how='left')
df = df.merge(gdp_melted, on=['entity', 'year'], how='left')

# === 5. Calculate Metrics ===
df['emissions_per_capita'] = df['total_emissions'] / df['population']
df['emissions_per_gdp'] = df['total_emissions'] / df['gdp']

# === 6. Export Final Dataset for Power BI or Tableau ===
df.to_csv("co2_emissions_per_capita_and_gdp.csv", index=False)