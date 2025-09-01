import uuid
from datetime import date, datetime
from typing import Optional

##################################### models_fact


class FactRecipe(FactBaseModel):
    new_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    id: int
    flow_reference: str
    region_reference: str
    unit_reference: str
    flow_input: str
    region_inflow: str | None = None
    value_inflow: float | None = None
    unit_inflow: str | None = None
    value_emission: float
    unit_emission: str
    metrics: str

    class Config:
        from_attributes = True


class UnitConverter(BaseModel):
    unit_from_update: str | None = (
        None  # Assuming this is a foreign key relationship in Django
    )
    unit_to_update: str | None = (
        None  # Assuming this is a foreign key relationship in Django
    )
    unit_from: str
    unit_to: str
    multiplier: float
    unit_type: str

    def __str__(self) -> str:
        return f"{self.unit_from} - {self.unit_to}"

    class Config:
        from_attributes = True


#################################### models_dim


class DimProductDjango(ModelDimDjango):
    code = models.CharField(max_length=20, null=False, primary_key=True)
    name = models.CharField(max_length=200, null=True, unique=True)
    parent_name = models.ForeignKey(
        "self",
        to_field="name",
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    description = models.TextField(null=True, unique=True)

    def __str__(self) -> str:
        return f"{self.description}"

    class Meta:
        db_table = "dim_product"
        verbose_name = "Product Classification"


############################################ models_corr


class CorrespondenceDjango(models.Model):
    created_by = models.ForeignKey(
        to=UserDjango,
        to_field="email",
        related_name="%(class)s",
        on_delete=models.SET_NULL,
        null=True,
    )
    create_time = models.DateField(null=False, default=date.today)

    class Meta:
        abstract = True


class ProductCorrespondenceDjango(CorrespondenceDjango):
    external_name = models.CharField(null=False, max_length=200)
    external_description = models.TextField(null=True)
    base_name = models.ForeignKey(
        to=DimProduct, to_field="name", on_delete=models.SET_NULL, null=True
    )

    def __str__(self) -> str:
        return f"{self.external_name} - {self.base_name}"

    class Meta:
        db_table = "corr_product"
        verbose_name = "Product Correspondence"


############################# datahub


class DatasetMeta(BaseModel):
    name: str = Field(..., max_length=255)
    acronym: str = Field(..., max_length=10)
    version_date: date
    version_semantic: Optional[str] = Field(None, max_length=10)
    is_latest: bool = True
    create_time: datetime = Field(default_factory=datetime.now)
    created_by: Optional[User] = None
    comment: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.name} - {self.acronym}"


class DatasetMetaDjango(models.Model):
    name = models.CharField(max_length=255, null=False)
    acronym = models.CharField(max_length=10, null=False)
    version_date = models.DateField(null=False)
    version_semantic = models.CharField(max_length=10, null=True)
    is_latest = models.BooleanField(default=True, null=False)
    create_time = models.DateTimeField(null=False, auto_now_add=True)
    created_by = models.ForeignKey(
        to=UserDjango,
        to_field="email",
        related_name="dataset",
        on_delete=models.SET_NULL,
        null=True,
    )
    comment = models.TextField(null=True)

    class Meta:
        db_table = "dataset_meta"
        verbose_name = "Meta Data"
        verbose_name_plural = "Meta Data"


################# footprint_analyzer


class CountryFootprintDjango(FactBaseModel):
    act_code = models.ForeignKey(
        to=DimActivityDjango, to_field="code", null=False, on_delete=models.CASCADE
    )
    region_code = models.ForeignKey(
        to=DimRegionDjango, to_field="code", null=False, on_delete=models.CASCADE
    )
    value = models.FloatField(null=False)
    unit_emission = models.ForeignKey(
        to=DimUnitDjango,
        to_field="short_name",
        null=False,
        default="tonnes CO2eq",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.act_code}-{self.region_code}"

    class Meta:
        db_table = "fact_country_footprint"
        verbose_name = "Country Footprint"


class CountryRecipeDjango(FactBaseModelDjango):
    product_code = models.ForeignKey(
        to=DimProductDjango,
        to_field="code",
        null=True,
        on_delete=models.SET_NULL,
    )
    unit_reference = models.ForeignKey(
        to=DimUnitDjango,
        to_field="short_name",
        null=True,
        on_delete=models.SET_NULL,
        related_name="unit_reference",
    )
    act_code = models.ForeignKey(
        to=DimActivityDjango, to_field="code", null=False, on_delete=models.CASCADE
    )
    region_code = models.ForeignKey(
        to=DimRegionDjango, to_field="code", null=False, on_delete=models.CASCADE
    )
    value = models.FloatField(null=False)
    unit_emission = models.ForeignKey(
        to=DimUnitDjango,
        to_field="short_name",
        null=False,
        default="tonnes CO2eq",
        on_delete=models.CASCADE,
        related_name="unit_emission",
    )

    class Meta:
        db_table = "fact_ctry_recipe"
        verbose_name = "Country Footprint Recipe"
