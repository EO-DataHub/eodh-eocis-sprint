import climdc as ec

prods = ec.list_products()
print(prods)

datasets = ec.find_datasets(product="ukcp")
print(datasets)

ds = ec.load(datasets[0],
     measurements=["tas", "pr"],
     time=("2023-01-01", "2023-03-30"),
     x=[-10000, 62000], y=[2000, 230000]
)

print(ds)
print("\nIs it ever appropriate to load these into a single Xarray Dataset? "
 "Even if different time frequencies?")

"""
import datacube

dc = datacube.Datacube(app="my_analysis")

datasets = dc.find_datasets(
    product="ls9_sr",
    x=(29.0, 29.01),
    y=(25.0, 25.01),
    time=("2022-01-01", "2022-02-01"),
)

ds = dc.load(
    datasets=datasets,
    measurements=["red", "green", "blue"],
    output_crs="EPSG:6933",
    resolution=(-30, 30),
)
ds
"""

