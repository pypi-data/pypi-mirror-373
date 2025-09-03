from datetime import datetime as Datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal

from pydantic import BaseModel, Extra, Field

EXPRESSION_DESCRIPTION = "The expression to create the desired band. " + \
    "Can be a band of the data prefaced by its alias (ie 'S2.B05', " + \
    "'S2.B12') or an operation on the bands (ie 'S2.B5 + S2.B8')."
UNIT_DESCRIPTION = "The unit of the requested band."
MIN_DESCRIPTION = "A minimum value to clip the band values."
MAX_DESCRIPTION = "A maximum value to clip the band values."
RGB_DESCRIPTION = "Which RGB channel the band is used for the preview. " + \
    "Value can be 'RED', 'GREEN' or 'BLUE'."
CMAP_DESCRIPTION = "The matplotlib color map to use for the preview."


class ColorMap(str, Enum):
    viridis = "viridis"
    plasma = "plasma"
    inferno = "inferno"
    magma = "magma"
    cividis = "cividis"
    Greys = "Greys"
    Purples = "Purples"
    Blues = "Blues"
    Greens = "Greens"
    Oranges = "Oranges"
    Reds = "Reds"
    YlOrBr = "YlOrBr"
    YlOrRd = "YlOrRd"
    OrRd = "OrRd"
    PuRd = "PuRd"
    RdPu = "RdPu"
    BuPu = "BuPu"
    GnBu = "GnBu"
    PuBu = "PuBu"
    YlGnBu = "YlGnBu"
    PuBuGn = "PuBuGn"
    BuGn = "BuGn"
    YlGn = "YlGn"
    binary = "binary"
    gray = "gray"
    bone = "bone"
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"
    cool = "cool"
    hot = "hot"
    rainbow = "rainbow"
    gist_rainbow = "gist_rainbow"
    ocean = "ocean"


class RGB(str, Enum):
    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'


class ChunkingStrategy(str, Enum):
    CARROT = 'carrot'
    POTATO = 'potato'
    SPINACH = 'spinach'


class SensorFamily(str, Enum):
    OPTIC = "OPTIC"
    RADAR = "RADAR"
    MULTI = "MULTI"
    UNKNOWN = "UNKNOWN"


class MimeType(Enum):
    TIFF = "image/tiff"
    XML = "text/xml"
    JPG = "image/jpg"
    PNG = "image/png"
    GIF = "image/gif"
    JSON = "application/json"
    PDF = "application/pdf"
    PVL = "text/pvl"
    TEXT = "text/plain"
    MARKDOWN = "text/markdown"
    GML = "application/gml+xml"
    COG = "image/tiff; application=geotiff; profile=cloud-optimized"
    FLATGEOBUF = "application/vnd.flatgeobuf"  # https://github.com/flatgeobuf/flatgeobuf/discussions/112#discussioncomment-4606721  # noqa
    GEOJSON = "application/geo+json"
    GEOPACKAGE = "application/geopackage+sqlite3"
    GEOTIFF = "image/tiff; application=geotiff"
    HDF = "application/x-hdf"  # Hierarchical Data Format versions 4 and earlier.
    HDF5 = "application/x-hdf5"  # Hierarchical Data Format version 5
    HTML = "text/html"
    JPEG = "image/jpeg"
    JPEG2000 = "image/jp2"
    PARQUET = "application/x-parquet"  # https://github.com/opengeospatial/geoparquet/issues/115#issuecomment-1181549523
    KML = "application/vnd.google-earth.kml+xml"
    ZARR = "application/vnd+zarr"  # https://github.com/openMetadataInitiative/openMINDS_core/blob/v4/instances/data/contentTypes/zarr.jsonld
    NETCDF = "application/netcdf"  # https://github.com/Unidata/netcdf/issues/42#issuecomment-1007618822
    ZIP = "application/zip"


class ProcessingLevel(Enum):
    RAW = "RAW"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class ObservationType(Enum):
    optic = "OPTIC"
    image = "IMAGE"
    radar = "RADAR"
    dem = "DEM"
    other = "OTHER"


class ResourceType(Enum):
    cube = "CUBE"
    gridded = "GRIDDED"
    vector = "VECTOR"
    other = "OTHER"


class ItemFormat(Enum):
    adc3 = "adc3"
    shape = "SHAPE"
    dimap = "DIMAP"
    geotiff = "GEOTIFF"
    jpeg2000 = "JPEG2000"
    safe = "SAFE"
    theia = "THEIA"
    ast_dem = "AST_DEM"
    digitalglobe = "DIGITALGLOBE"
    geoeye = "GEOEYE"
    rapideye = "RAPIDEYE"
    spot5 = "SPOT5"
    spot6_7 = "SPOT6_7"
    other = "OTHER"
    terrasar = "TerraSAR-X"
    csk = "COSMO-SkyMed"
    umbra = "UMBRA"
    bsg = "BlackSkyGlobal"


class AssetFormat(Enum):
    shape = "SHAPE"
    gml = "GML"
    geotiff = "GEOTIFF"
    tfw = "TFW"
    j2w = "J2W"
    jpg = "JPG"
    jpg2000 = "JPG2000"
    png = "PNG"
    pdf = "PDF"
    csv = "CSV"
    json = "JSON"
    zip = "ZIP"
    tar = "TAR"
    targz = "TARGZ"
    other = "OTHER"
    xml = "XML"
    txt = "TEXT"
    pvl = "PVL"
    yaml = "YAML"
    geojson = "GEOJSON"
    cog = "COG"
    zarr = "ZARR"
    gif = "GIF"


class SensorType(str, Enum):
    SAR = "SAR"


class Role(Enum):
    airs_item = "airs_item"
    thumbnail = "thumbnail"
    overview = "overview"
    data = "data"
    metadata = "metadata"
    cog = "cog"
    zarr = "zarr"
    datacube = "datacube"
    visual = "visual"
    date = "date"
    graphic = "graphic"
    data_mask = "data-mask"
    snow_ice = "snow-ice"
    land_water = "land-water"
    water_mask = "water-mask"
    iso_19115 = "iso-19115"
    reflectance = "reflectance"
    temperature = "temperature"
    saturation = "saturation"
    cloud = "cloud"
    cloud_shadow = "cloud-shadow"
    incidence_angle = "incidence-angle"
    azimuth = "azimuth"
    sun_azimuth = "sun-azimuth"
    sun_elevation = "sun-elevation"
    terrain_shadow = "terrain-shadow"
    terrain_occlusion = "terrain-occlusion"
    terrain_illumination = "terrain-illumination"
    local_incidence_angle = "local-incidence-angle"
    noise_power = "noise-power"
    amplitude = "amplitude"
    magnitude = "magnitude"
    sigma0 = "sigma0"
    beta0 = "beta0"
    gamma0 = "gamma0"
    date_offset = "date-offset"
    covmat = "covmat"
    prd = "prd"
    extent = "extent"
    pan_sharpened = "pan-sharpened"


class CommonBandName(Enum):
    coastal = "coastal"
    blue = "blue"
    green = "green"
    red = "red"
    yellow = "yellow"
    pan = "pan"
    rededge = "rededge"
    nir = "nir"
    nir08 = "nir08"
    nir09 = "nir09"
    cirrus = "cirrus"
    swir16 = "swir16"
    swir22 = "swir22"
    lwir = "lwir"
    lwir11 = "lwir11"
    lwir12 = "lwir12"


class DimensionType(str, Enum):
    spatial = "spatial"
    temporal = "temporal"
    geometry = "geometry"


class HorizontalSpatialDimension(BaseModel):
    axis: str = Field()
    description: str = Field()
    type: Literal[DimensionType.spatial] = DimensionType.spatial.value
    extent: list[float | int] = Field()
    step: float | int | None = Field(default=None)
    reference_system: str | int | Any = Field(default=4326)


class TemporalDimension(BaseModel):
    axis: str = Field()
    description: str = Field()
    type: Literal[DimensionType.temporal] = DimensionType.temporal.value
    extent: list[str] | None = Field(default=None)
    step: str | None = Field(default=None)


Dimension = Annotated[HorizontalSpatialDimension | TemporalDimension,
                      Field(discriminator="type")]


class VariableType(str, Enum):
    data = "data"
    auxiliary = "auxiliary"


class Variable(BaseModel):
    dimensions: list[str] = Field()
    type: VariableType = Field()
    description: str | None = Field(default=None)
    extent: list[float | int | str] = Field()
    unit: str | None = Field(default=None)
    expression: str = Field()


class Indicators(BaseModel):
    dc3__time_compacity: float = Field(default=None, title="[ARLAS, extension dc3] Indicates whether the temporal extent of the temporal slices (groups) are compact or not compared to the cube temporal extent. Computed as follow: 1-range(group rasters) / range(cube rasters).")
    dc3__spatial_coverage: float = Field(default=None, title="[ARLAS, extension dc3] Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))")
    dc3__group_lightness: float = Field(default=None, title="[ARLAS, extension dc3] Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))")
    dc3__time_regularity: float = Field(default=None, title="[ARLAS, extension dc3] Indicates the regularity of the extents between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)")


class ItemReference(BaseModel):
    dc3__collection: str = Field(description="[ARLAS, extension dc3] Name of the collection containing the item")
    dc3__id: str = Field(description="[ARLAS, extension dc3] Item's identifer")
    dc3__alias: str = Field(description="[ARLAS, extension dc3] Product alias (e.g. s2_l2)")


class ItemGroup(BaseModel):
    dc3__references: list[ItemReference] = Field(title="[ARLAS, extension dc3] The rasters of this group.", min_length=1)
    dc3__datetime: Datetime = Field(title="[ARLAS, extension dc3] The date time of this temporal group.")
    dc3__quality_indicators: Indicators | None = Field(default=None, title="[ARLAS, extension dc3] Set of indicators for estimating the quality of the datacube group. The indicators are group based.")


class Band(BaseModel, extra=Extra.allow):
    index: int = Field(default=None, ge=1, title="[ARLAS] Band index within the asset, starting at 1")
    asset: str = Field(default=None, title="[ARLAS] Name of the asset, must be present in `item.assets`")
    path_within_asset: str = Field(default=None, title="[ARLAS] If the band is nested within a sub file of the asset (e.g. tgz, zip), then the path within the asset must be provided, undefined otherwise.")
    variable_value_alias: dict[float, str] = Field(default=None, title="[ARLAS] Dictionary of value->alias for bands encoding semantic tags (e.g land cover classification)")
    name: str = Field(title="[STAC] The name of the band (e.g., B01, B8, band2, red).", max_length=300)
    eo__common_name: str = Field(default=None, title="[STAC, extension eo] The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.")
    description: str = Field(default=None, title="[STAC] Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.", max_length=300)
    eo__center_wavelength: float = Field(default=None, title="[STAC, extension eo] The center wavelength of the band, in micrometers (μm).")
    eo__full_width_half_max: float = Field(default=None, title="[STAC, extension eo] Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).")
    eo__solar_illumination: float = Field(default=None, title="[STAC, extension eo] The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.")
    dc3__quality_indicators: Indicators = Field(default=None, title="[ARLAS, extension dc3] Set of indicators for estimating the quality of the datacube variable (band).")
    dc3__expression: str = Field(default=None, description=EXPRESSION_DESCRIPTION)
    dc3__unit: str = Field(default=None, description=UNIT_DESCRIPTION)
    dc3__min: float = Field(default=None, description=MIN_DESCRIPTION)
    dc3__max: float = Field(default=None, description=MAX_DESCRIPTION)
    dc3__rgb: RGB | None = Field(default=None, description=RGB_DESCRIPTION)
    dc3__cmap: ColorMap | None = Field(default=None, description=CMAP_DESCRIPTION)


class Asset(BaseModel, extra=Extra.allow):
    name: str | None = Field(default=None, title="[ARLAS] Asset's name. Must be the same as the key in the `assets` dictionary.", max_length=300)
    size: int | None = Field(default=None, title="[ARLAS] Asset's size in Bytes.")
    href: str | None = Field(default=None, title="[STAC] Absolute link to the asset object.")
    asset_type: str | None = Field(default=None, title="[ARLAS] Type of data (ResourceType)")
    asset_format: str | None = Field(default=None, title="[ARLAS] Data format (AssetFormat)")
    storage__requester_pays: bool | None = Field(default=None, title="[STAC, extension storage]Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets")
    storage__tier: str | None = Field(default=None, title="[STAC, extension storage]Cloud Provider Storage Tiers (Standard, Glacier, etc.)")
    storage__platform: str | None = Field(default=None, title="[STAC, extension storage]PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)")
    storage__region: str | None = Field(default=None, title="[STAC, extension storage]The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)")
    airs__managed: bool | None = Field(default=True, title="[ARLAS, extension AIRS] Whether the asset is managed by AIRS or not.")
    airs__object_store_bucket: str | None = Field(default=None, title="[ARLAS, extension AIRS] Object store bucket for the asset object.")
    airs__object_store_key: str | None = Field(default=None, title="[ARLAS, extension AIRS] Object store key of the asset object.")
    title: str | None = Field(default=None, title="[STAC] Optional displayed title for clients and users.", max_length=300)
    description: str | None = Field(default=None, title="[STAC] A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.", max_length=300)
    type: str | None = Field(default=None, title="[STAC] Optional description of the media type. Registered Media Types are preferred. See MimeType for common media types.", max_length=300)
    roles: List[str] | None = Field(default=None, title="[STAC] Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.", min_length=1, max_length=300)
    extra_fields: Dict[str, Any] | None = Field(default=None, title="[ARLAS] Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.")
    gsd: float | None = Field(default=None, title="[deprecated, use eo:gsd instead] Ground Sampling Distance (resolution) of the asset")
    eo__gsd: float | None = Field(default=None, title="[STAC, extension eo] Ground Sampling Distance (resolution)")
    eo__bands: List[Band] | None = Field(default=None, title="[STAC, extension eo] An array of available bands where each object is a Band Object. If given, requires at least one band.", )
    sar__instrument_mode: str | None = Field(default=None, title="[STAC, extension sar] The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for \"Wave mode\" of Sentinel-1 and Envisat ASAR satellites.")
    sar__frequency_band: str | None = Field(default=None, title="[STAC, extension sar] The common name for the frequency band to make it easier to search for bands across instruments. See section \"Common Frequency Band Names\" for a list of accepted names.")
    sar__center_frequency: float | None = Field(default=None, title="[STAC, extension sar] The center frequency of the instrument, in gigahertz (GHz).")
    sar__polarizations: list[str] | None = Field(default=None, title="[STAC, extension sar] Any combination of polarizations.")
    sar__product_type: str | None = Field(default=None, title="[STAC, extension sar] The product type, for example SSC, MGD, or SGC")
    sar__resolution_range: float | None = Field(default=None, title="[STAC, extension sar] The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).")
    sar__resolution_azimuth: float | None = Field(default=None, title="[STAC, extension sar] The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).")
    sar__pixel_spacing_range: float | None = Field(default=None, title="[STAC, extension sar] The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.")
    sar__pixel_spacing_azimuth: float | None = Field(default=None, title="[STAC, extension sar] The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.")
    sar__looks_range: float | None = Field(default=None, title="[STAC, extension sar] Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.")
    sar__looks_azimuth: float | None = Field(default=None, title="[STAC, extension sar] Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.")
    sar__looks_equivalent_number: float | None = Field(default=None, title="[STAC, extension sar] The equivalent number of looks (ENL).")
    sar__observation_direction: str | None = Field(default=None, title="[STAC, extension sar] Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.")
    proj__epsg: int | None = Field(default=None, title="[STAC, extension proj] EPSG code of the datasource.")
    proj__wkt2: str | None = Field(default=None, title="[STAC, extension proj] PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.")
    proj__geometry: Any | None = Field(default=None, title="[STAC, extension proj] Defines the footprint of this Item.")
    proj__bbox: List[float] | None = Field(default=None, title="[STAC, extension proj] Bounding box of the Item in the asset CRS in 2 or 3 dimensions.")
    proj__centroid: Any | None = Field(default=None, title="[STAC, extension proj] Coordinates representing the centroid of the Item (in lat/long).")
    proj__shape: List[float] | None = Field(default=None, title="[STAC, extension proj] Number of pixels in Y and X directions for the default grid.")
    proj__transform: List[float] | None = Field(default=None, title="[STAC, extension proj] The affine transformation coefficients for the default grid.")


class Properties(BaseModel, extra=Extra.allow):
    datetime: Datetime | None = Field(default=None, title="[STAC] datetime associated with this item. If None, a start_datetime and end_datetime must be supplied.")
    start_datetime: Datetime | None = Field(default=None, title="[STAC] Optional start datetime, part of common metadata. This value will override any start_datetime key in properties.")
    end_datetime: Datetime | None = Field(default=None, title="[STAC] Optional end datetime, part of common metadata. This value will override any end_datetime key in properties.")
    keywords: List[str] | None = Field(default=None, title="STAC] A list of keywords")
    programme: str | None = Field(default=None, title="[ARLAS] Name of the programme")
    constellation: str | None = Field(default=None, title="[ARLAS] Name of the constellation")
    satellite: str | None = Field(default=None, title="[ARLAS] Name of the satellite")
    platform: str | None = Field(default=None, title="[ARLAS] Name of the satellite platform")
    instrument: str | None = Field(default=None, title="[ARLAS] Name of the instrument")
    sensor: str | None = Field(default=None, title="[ARLAS] Name of the sensor")
    sensor_mode: str | None = Field(default=None, title="[ARLAS] Mode of the sensor during acquisition")
    sensor_type: str | None = Field(default=None, title="[ARLAS] Type of sensor")
    license: str | None = Field(default=None, title="[STAC] License(s) of the data as SPDX License identifier, SPDX License expression, or other.")
    annotations: str | None = Field(default=None, title="[ARLAS] Human annotations for the item")
    gsd: float | None = Field(default=None, title="[deprecated, use eo:gsd instead] Ground Sampling Distance (resolution)")
    secondary_id: str | None = Field(default=None, title="[ARLAS] Secondary identifier")
    data_type: str | None = Field(default=None, title="[ARLAS] Type of data")
    item_type: str | None = Field(default=None, title="[ARLAS] Type of data (ResourceType)")
    item_format: str | None = Field(default=None, title="[ARLAS] Data format (ItemFormat)")
    main_asset_format: str | None = Field(default=None, title="[ARLAS] Data format of the main asset (AssetFormat)")
    main_asset_name: str | None = Field(default=None, title="[ARLAS] Name of the main asset (Role)")
    observation_type: str | None = Field(default=None, title="[ARLAS] Type of observation (ObservationType)")
    data_coverage: float | None = Field(default=None, title="[ARLAS] Estimate of data cover")
    water_coverage: float | None = Field(default=None, title="[ARLAS] Estimate of water cover")
    locations: List[str] | None = Field(default=None, title="[ARLAS] List of locations covered by the item")
    create_datetime: int | None = Field(default=None, title="[ARLAS, AIRS]Date of item creation in the catalog, managed by the ARLAS Item Registration Service")
    update_datetime: int | None = Field(default=None, title="[ARLAS, AIRS]Update date of the item in the catalog, managed by the ARLAS Item Registration Service")
    created: int | None = Field(default=None, title="[STAC] Creation date and time of the corresponding STAC entity or Asset (see below), in UTC.")
    updated: int | None = Field(default=None, title="[STAC] Date and time the corresponding STAC entity or Asset (see below) was updated last, in UTC.")
    view__off_nadir: float | None = Field(default=None, title="[STAC, extension view] The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).")
    view__incidence_angle: float | None = Field(default=None, title="[STAC, extension view] The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).")
    view__azimuth: float | None = Field(default=None, title="[STAC, extension view] Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).")
    view__sun_azimuth: float | None = Field(default=None, title="[STAC, extension view] Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).")
    view__sun_elevation: float | None = Field(default=None, title="[STAC, extension view] Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° means the data was captured during nautical twilight.")
    storage__requester_pays: bool | None = Field(default=None, title="[STAC, extension storage] Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets")
    storage__tier: str | None = Field(default=None, title="[STAC, extension storage] Cloud Provider Storage Tiers (Standard, Glacier, etc.)")
    storage__platform: str | None = Field(default=None, title="[STAC, extension storage] PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)")
    storage__region: str | None = Field(default=None, title="[STAC, extension storage] The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)")
    eo__cloud_cover: float | None = Field(default=None, title="[STAC, extension eo] Estimate of cloud cover.")
    eo__snow_cover: float | None = Field(default=None, title="[STAC, extension eo] Estimate of snow and ice cover.")
    eo__bands: List[Band] | None = Field(default=None, title="[STAC, extension eo] An array of available bands where each object is a Band Object. If given, requires at least one band.")
    processing__expression: str | None = Field(default=None, title="[STAC, extension processing] An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).")
    processing__lineage: str | None = Field(default=None, title="[STAC, extension processing] Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.")
    processing__level: str | None = Field(default=None, title="[STAC, extension processing] The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).")
    processing__facility: str | None = Field(default=None, title="[STAC, extension processing] The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.")
    processing__software: Dict[str, str] | None = Field(default=None, title="[STAC, extension processing] A dictionary with name/version for key/value describing one or more softwares that produced the data.")
    dc3__quality_indicators: Indicators | None = Field(default=None, title="[STAC, extension dc3] Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.")
    dc3__composition: List[ItemGroup] | None = Field(default=None, title="[STAC, extension dc3] List of item groups used for elaborating the cube temporal slices.")
    dc3__number_of_chunks: int | None = Field(default=None, title="[STAC, extension dc3] Number of chunks (if zarr or similar partitioned format) within the cube.")
    dc3__chunk_weight: int | None = Field(default=None, title="[STAC, extension dc3] Weight of a chunk (number of bytes).")
    dc3__fill_ratio: float | None = Field(default=None, title="[STAC, extension dc3] 1: the cube is full, 0 the cube is empty, in between the cube is partially filled.")
    dc3__overview: dict[str, str] | dict[RGB, str] | None = Field(default=None, title="[STAC, extension dc3] Parameters used to generate the preview. Either contains the matplotlib colormap and the band used, or the mapping between RGB bands and the datacube's bands used.")
    cube__dimensions: Dict[str, Dimension] | None = Field(default=None, title="[STAC, extension cube] Uniquely named dimensions of the datacube.")
    cube__variables: Dict[str, Variable] | None = Field(default=None, title="[STAC, extension cube] Uniquely named variables of the datacube.")
    acq__acquisition_mode: str | None = Field(default=None, title="[STAC, extension acq] The name of the acquisition mode.")
    acq__acquisition_orbit_direction: str | None = Field(default=None, title="[STAC, extension acq] Acquisition orbit direction (ASCENDING or DESCENDING).")
    acq__acquisition_type: str | None = Field(default=None, title="[STAC, extension acq] Acquisition type (STRIP)")
    acq__acquisition_orbit: float | None = Field(default=None, title="[STAC, extension acq] Acquisition orbit")
    acq__across_track: float | None = Field(default=None, title="[STAC, extension acq] Across track angle")
    acq__along_track: float | None = Field(default=None, title="[STAC, extension acq] Along track angle")
    acq__archiving_date: Datetime | None = Field(default=None, title="[STAC, extension acq] Archiving date")
    acq__download_orbit: float | None = Field(default=None, title="[STAC, extension acq] Download orbit")
    acq__request_id: str | None = Field(default=None, title="[STAC, extension acq] Original request identifier")
    acq__quality_average: float | None = Field(default=None, title="[STAC, extension acq] Quality average")
    acq__quality_computation: str | None = Field(default=None, title="[STAC, extension acq] Quality computation")
    acq__receiving_station: str | None = Field(default=None, title="[STAC, extension acq] Receiving station")
    acq__reception_date: Datetime | None = Field(default=None, title="[STAC, extension acq] Reception date")
    acq__spectral_mode: str | None = Field(default=None, title="[STAC, extension acq] Spectral mode")
    sar__instrument_mode: str | None = Field(default=None, title="[STAC, extension sar] The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for \"Wave mode\" of Sentinel-1 and Envisat ASAR satellites.")
    sar__frequency_band: str | None = Field(default=None, title="[STAC, extension sar] The common name for the frequency band to make it easier to search for bands across instruments. See section \"Common Frequency Band Names\" for a list of accepted names.")
    sar__center_frequency: float | None = Field(default=None, title="[STAC, extension sar] The center frequency of the instrument, in gigahertz (GHz).")
    sar__polarizations: list[str] | None = Field(default=None, title="[STAC, extension sar] Any combination of polarizations.")
    sar__product_type: str | None = Field(default=None, title="[STAC, extension sar] The product type, for example SSC, MGD, or SGC")
    sar__resolution_range: float | None = Field(default=None, title="[STAC, extension sar] The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).")
    sar__resolution_azimuth: float | None = Field(default=None, title="[STAC, extension sar] The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).")
    sar__pixel_spacing_range: float | None = Field(default=None, title="[STAC, extension sar] The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.")
    sar__pixel_spacing_azimuth: float | None = Field(default=None, title="[STAC, extension sar] The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.")
    sar__looks_range: float | None = Field(default=None, title="[STAC, extension sar] Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.")
    sar__looks_azimuth: float | None = Field(default=None, title="[STAC, extension sar] Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.")
    sar__looks_equivalent_number: float | None = Field(default=None, title="[STAC, extension sar] The equivalent number of looks (ENL).")
    sar__observation_direction: str | None = Field(default=None, title="[STAC, extension sar] Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.")
    proj__epsg: int | None = Field(default=None, title="[STAC, extension proj] EPSG code of the datasource.")
    proj__wkt2: str | None = Field(default=None, title="[STAC, extension proj] PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.")
    proj__geometry: Any | None = Field(default=None, title="[STAC, extension proj] Defines the footprint of this Item.")
    proj__bbox: List[float] | None = Field(default=None, title="[STAC, extension proj] Bounding box of the Item in the asset CRS in 2 or 3 dimensions.")
    proj__centroid: Any | None = Field(default=None, title="[STAC, extension proj] Coordinates representing the centroid of the Item (in lat/long).")
    proj__shape: List[float] | None = Field(default=None, title="[STAC, extension proj] Number of pixels in Y and X directions for the default grid.")
    proj__transform: List[float] | None = Field(default=None, title="[STAC, extension proj] The affine transformation coefficients for the default grid.")
    generated__has_overview: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has an overview or not.")
    generated__has_thumbnail: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has a thumbnail or not.")
    generated__has_metadata: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has a metadata file or not.")
    generated__has_data: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has a data file or not.")
    generated__has_cog: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has a cog or not.")
    generated__has_zarr: bool | None = Field(default=False, title="[ARLAS, AIRS] Whether the item has a zarr or not.")
    generated__date_keywords: List[str] | None = Field(default=None, title="[ARLAS, AIRS] A list of keywords indicating clues on the date")
    generated__day_of_week: int | None = Field(default=None, title="[ARLAS, AIRS] Day of week.")
    generated__day_of_year: int | None = Field(default=None, title="[ARLAS, AIRS] Day of year.")
    generated__hour_of_day: int | None = Field(default=None, title="[ARLAS, AIRS] Hour of day.")
    generated__minute_of_day: int | None = Field(default=None, title="[ARLAS, AIRS] Minute of day.")
    generated__month: int | None = Field(default=None, title="[ARLAS, AIRS] Month")
    generated__year: int | None = Field(default=None, title="[ARLAS, AIRS] Year")
    generated__season: str | None = Field(default=None, title="[ARLAS, AIRS] Season")
    generated__tltrbrbl: List[List[float]] | None = Field(default=None, title="[ARLAS, AIRS] The coordinates of the top left, top right, bottom right, bottom left corners of the item.")
    generated__band_common_names: List[str] | None = Field(default=None, title="[ARLAS, AIRS] List of the band common names.")
    generated__band_names: List[str] | None = Field(default=None, title="[ARLAS, AIRS] List of the band names.")
    generated__geohash2: str | None = Field(default=None, title="[ARLAS, AIRS] Geohash on the first two characters.")
    generated__geohash3: str | None = Field(default=None, title="[ARLAS, AIRS] Geohash on the first three characters.")
    generated__geohash4: str | None = Field(default=None, title="[ARLAS, AIRS] Geohash on the first four characters.")
    generated__geohash5: str | None = Field(default=None, title="[ARLAS, AIRS] Geohash on the first five characters.")


class Item(BaseModel, extra=Extra.allow):
    collection: str | None = Field(default=None, title="[STAC] Name of the collection the item belongs to.", max_length=300)
    catalog: str | None = Field(default=None, title="Name of the catalog the item belongs to.", max_length=300)
    id: str | None = Field(default=None, title="[STAC] Unique item identifier. Must be unique within the collection.", max_length=300)
    geometry: Dict[str, Any] | None = Field(default=None, title="[STAC] Defines the full footprint of the asset represented by this item, formatted according to `RFC 7946, section 3.1 (GeoJSON) <https://tools.ietf.org/html/rfc7946>`_")
    bbox: List[float] | None = Field(default=None, title="[STAC] Bounding Box of the asset represented by this item using either 2D or 3D geometries. The length of the array must be 2*n where n is the number of dimensions. Could also be None in the case of a null geometry.")
    centroid: List[float] | None = Field(default=None, title="Coordinates (lon/lat) of the geometry's centroid.")
    assets: Dict[str, Asset] | None = Field(default=None, title="[STAC] A dictionary mapping string keys to Asset objects. All Asset values in the dictionary will have their owner attribute set to the created Item.")
    properties: Properties | None = Field(default=None, title="[STAC] Item properties")
