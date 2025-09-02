from .attribute_description import AttributeDescription_V1_0_1
from .attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from .base_attribute import BaseAttribute_V1_0_0
from .base_category_attribute import BaseCategoryAttribute_V1_0_0
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0
from .base_object_properties import (
    BaseObjectProperties_V1_0_1,
    BaseObjectProperties_V1_0_1_Uuid,
    BaseObjectProperties_V1_1_0,
    BaseObjectProperties_V1_1_0_Uuid,
)
from .base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from .block_model_attribute import BlockModelAttribute_V1_0_0
from .block_model_category_attribute import BlockModelCategoryAttribute_V1_0_0
from .block_model_flexible_structure import BlockModelFlexibleStructure_V1_0_0
from .block_model_fully_subblocked_structure import BlockModelFullySubblockedStructure_V1_0_0
from .block_model_regular_structure import BlockModelRegularStructure_V1_0_0
from .block_model_variable_octree_structure import BlockModelVariableOctreeStructure_V1_0_0
from .bool_attribute import BoolAttribute_V1_0_1, BoolAttribute_V1_1_0
from .bool_time_series import BoolTimeSeries_V1_0_1, BoolTimeSeries_V1_1_0
from .bounding_box import BoundingBox_V1_0_1
from .brep_container import BrepContainer_V1_0_1, BrepContainer_V1_0_1_Brep
from .category_attribute import CategoryAttribute_V1_0_1, CategoryAttribute_V1_1_0
from .category_attribute_description import CategoryAttributeDescription_V1_0_1
from .category_data import CategoryData_V1_0_1
from .category_ensemble import CategoryEnsemble_V1_0_1, CategoryEnsemble_V1_1_0
from .category_time_series import CategoryTimeSeries_V1_0_1, CategoryTimeSeries_V1_1_0
from .channel_attribute import (
    ChannelAttribute_V1_0_1,
    ChannelAttribute_V1_0_1_Attribute,
    ChannelAttribute_V1_1_0,
    ChannelAttribute_V1_1_0_Attribute,
)
from .color_attribute import ColorAttribute_V1_0_0, ColorAttribute_V1_1_0
from .continuous_attribute import ContinuousAttribute_V1_0_1, ContinuousAttribute_V1_1_0
from .continuous_ensemble import ContinuousEnsemble_V1_0_1, ContinuousEnsemble_V1_1_0
from .continuous_time_series import ContinuousTimeSeries_V1_0_1, ContinuousTimeSeries_V1_1_0
from .crs import Crs_V1_0_1, Crs_V1_0_1_EpsgCode, Crs_V1_0_1_OgcWkt
from .cumulative_distribution_function import (
    CumulativeDistributionFunction_V1_0_1,
    CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation,
    CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel,
    CumulativeDistributionFunction_V1_0_1_LowerTailExtrapolation_PowerModel_PowerModel,
    CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation,
    CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel,
    CumulativeDistributionFunction_V1_0_1_UpperTailExtrapolation_PowerModel_PowerModel,
)
from .data_table import DataTable_V1_0_1, DataTable_V1_1_0, DataTable_V1_2_0
from .date_time_attribute import DateTimeAttribute_V1_0_1, DateTimeAttribute_V1_1_0
from .desurvey_method import DesurveyMethod_V1_0_0
from .distance_table import (
    DistanceTable_V1_0_1,
    DistanceTable_V1_0_1_Distance,
    DistanceTable_V1_1_0,
    DistanceTable_V1_1_0_Distance,
    DistanceTable_V1_2_0,
    DistanceTable_V1_2_0_Distance,
)
from .downhole_attributes import (
    DownholeAttributes_V1_0_0,
    DownholeAttributes_V1_0_0_Item,
    DownholeAttributes_V1_0_0_Item_DataTable,
    DownholeAttributes_V1_0_0_Item_DistanceTable,
    DownholeAttributes_V1_0_0_Item_IntervalTable,
    DownholeAttributes_V1_0_0_Item_RelativeLineationDataTable,
    DownholeAttributes_V1_0_0_Item_RelativePlanarDataTable,
)
from .downhole_direction_vector import DownholeDirectionVector_V1_0_0
from .ellipsoid import (
    Ellipsoid_V1_0_1,
    Ellipsoid_V1_0_1_EllipsoidRanges,
    Ellipsoid_V1_1_0,
    Ellipsoid_V1_1_0_EllipsoidRanges,
)
from .ellipsoids import Ellipsoids_V1_0_1
from .embedded_line_geometry import (
    EmbeddedLineGeometry_V1_0_0,
    EmbeddedLineGeometry_V1_0_0_Chunks,
    EmbeddedLineGeometry_V1_0_0_Vertices,
)
from .embedded_mesh_object import EmbeddedMeshObject_V1_0_0
from .embedded_polyline_object import EmbeddedPolylineObject_V1_0_0
from .embedded_triangulated_mesh import (
    EmbeddedTriangulatedMesh_V1_0_1,
    EmbeddedTriangulatedMesh_V1_1_0,
    EmbeddedTriangulatedMesh_V2_0_0,
    EmbeddedTriangulatedMesh_V2_0_0_Parts,
    EmbeddedTriangulatedMesh_V2_1_0,
    EmbeddedTriangulatedMesh_V2_1_0_Parts,
)
from .frequency_domain_electromagnetic_channel import (
    FrequencyDomainElectromagneticChannel_V1_0_0,
    FrequencyDomainElectromagneticChannel_V1_0_0_CoilConfiguration,
)
from .from_to import FromTo_V1_0_1
from .geometry_composite import GeometryComposite_V1_0_1
from .geometry_part import (
    GeometryPart_V1_0_1,
    GeometryPart_V1_0_1_Feature,
    GeometryPart_V1_0_1_Geometry,
    GeometryPart_V1_0_1_Geometry_PartKey,
)
from .hexahedrons import (
    Hexahedrons_V1_0_1,
    Hexahedrons_V1_0_1_Indices,
    Hexahedrons_V1_0_1_Vertices,
    Hexahedrons_V1_1_0,
    Hexahedrons_V1_1_0_Indices,
    Hexahedrons_V1_1_0_Vertices,
    Hexahedrons_V1_2_0,
    Hexahedrons_V1_2_0_Indices,
    Hexahedrons_V1_2_0_Vertices,
)
from .hole_chunks import HoleChunks_V1_0_0
from .hole_collars import HoleCollars_V1_0_0
from .indices_attribute import (
    IndicesAttribute_V1_0_1,
    IndicesAttribute_V1_0_1_RelatedObject,
    IndicesAttribute_V1_1_0,
    IndicesAttribute_V1_1_0_RelatedObject,
)
from .integer_attribute import IntegerAttribute_V1_0_1, IntegerAttribute_V1_1_0
from .interval_table import (
    IntervalTable_V1_0_1,
    IntervalTable_V1_0_1_FromTo,
    IntervalTable_V1_1_0,
    IntervalTable_V1_1_0_FromTo,
    IntervalTable_V1_2_0,
    IntervalTable_V1_2_0_FromTo,
)
from .intervals import Intervals_V1_0_1
from .lengths import Lengths_V1_0_1
from .lineage import (
    Lineage_V1_0_0,
    Lineage_V1_0_0_Runevent,
    Lineage_V1_0_0_Runevent_Inputdataset,
    Lineage_V1_0_0_Runevent_Inputdataset_Dataset,
    Lineage_V1_0_0_Runevent_Job,
    Lineage_V1_0_0_Runevent_Outputdataset,
    Lineage_V1_0_0_Runevent_Run,
)
from .lineation_data import LineationData_V1_0_1
from .lines_2d_indices import Lines2DIndices_V1_0_1, Lines2DIndices_V1_0_1_Indices
from .lines_3d_indices import Lines3DIndices_V1_0_1
from .locations import Locations_V1_0_1
from .material import Material_V1_0_1
from .mesh_quality import MeshQuality_V1_0_1
from .nan_categorical import NanCategorical_V1_0_1
from .nan_continuous import NanContinuous_V1_0_1
from .one_of_attribute import (
    OneOfAttribute_V1_0_1,
    OneOfAttribute_V1_0_1_Item,
    OneOfAttribute_V1_1_0,
    OneOfAttribute_V1_1_0_Item,
    OneOfAttribute_V1_2_0,
    OneOfAttribute_V1_2_0_Item,
)
from .planar_data import PlanarData_V1_0_1
from .polyline_2d import Polyline2D_V1_0_1
from .polyline_3d import Polyline3D_V1_0_1
from .quadrilaterals import (
    Quadrilaterals_V1_0_1,
    Quadrilaterals_V1_0_1_Indices,
    Quadrilaterals_V1_0_1_Vertices,
    Quadrilaterals_V1_1_0,
    Quadrilaterals_V1_1_0_Indices,
    Quadrilaterals_V1_1_0_Vertices,
    Quadrilaterals_V1_2_0,
    Quadrilaterals_V1_2_0_Indices,
    Quadrilaterals_V1_2_0_Vertices,
)
from .relative_lineation_data_table import (
    RelativeLineationDataTable_V1_0_1,
    RelativeLineationDataTable_V1_0_1_Distance,
    RelativeLineationDataTable_V1_1_0,
    RelativeLineationDataTable_V1_1_0_Distance,
    RelativeLineationDataTable_V1_2_0,
    RelativeLineationDataTable_V1_2_0_Distance,
)
from .relative_planar_data_table import (
    RelativePlanarDataTable_V1_0_1,
    RelativePlanarDataTable_V1_0_1_Distance,
    RelativePlanarDataTable_V1_1_0,
    RelativePlanarDataTable_V1_1_0_Distance,
    RelativePlanarDataTable_V1_2_0,
    RelativePlanarDataTable_V1_2_0_Distance,
)
from .resistivity_ip_dcip_survey_properties import ResistivityIpDcipSurveyProperties_V1_0_0
from .resistivity_ip_line import ResistivityIpLine_V1_1_0
from .resistivity_ip_phaseip_survey_properties import ResistivityIpPhaseipSurveyProperties_V1_0_0
from .resistivity_ip_pldp_configuration_properties import ResistivityIpPldpConfigurationProperties_V1_0_0
from .resistivity_ip_plpl_configuration_properties import ResistivityIpPlplConfigurationProperties_V1_0_0
from .resistivity_ip_sip_survey_properties import ResistivityIpSipSurveyProperties_V1_0_0
from .rotation import Rotation_V1_0_1, Rotation_V1_1_0
from .segments import (
    Segments_V1_0_1,
    Segments_V1_0_1_Indices,
    Segments_V1_0_1_Vertices,
    Segments_V1_1_0,
    Segments_V1_1_0_Indices,
    Segments_V1_1_0_Vertices,
    Segments_V1_2_0,
    Segments_V1_2_0_Indices,
    Segments_V1_2_0_Vertices,
)
from .string_attribute import StringAttribute_V1_0_1, StringAttribute_V1_1_0
from .surface_mesh import SurfaceMesh_V1_0_1
from .survey_line import (
    SurveyLine_V1_0_1,
    SurveyLine_V1_0_1_LocationChannels,
    SurveyLine_V1_1_0,
    SurveyLine_V1_1_0_LocationChannels,
)
from .tetrahedra import (
    Tetrahedra_V1_0_1,
    Tetrahedra_V1_0_1_Indices,
    Tetrahedra_V1_0_1_Vertices,
    Tetrahedra_V1_1_0,
    Tetrahedra_V1_1_0_Indices,
    Tetrahedra_V1_1_0_Vertices,
    Tetrahedra_V1_2_0,
    Tetrahedra_V1_2_0_Indices,
    Tetrahedra_V1_2_0_Vertices,
)
from .time_domain_electromagnetic_channel import (
    TimeDomainElectromagneticChannel_V1_0_0,
    TimeDomainElectromagneticChannel_V1_0_0_Filter,
)
from .time_step_attribute import TimeStepAttribute_V1_0_1, TimeStepAttribute_V1_1_0
from .time_step_continuous_attribute import TimeStepContinuousAttribute_V1_0_1, TimeStepContinuousAttribute_V1_1_0
from .time_step_date_time_attribute import TimeStepDateTimeAttribute_V1_0_1, TimeStepDateTimeAttribute_V1_1_0
from .triangles import (
    Triangles_V1_0_1,
    Triangles_V1_0_1_Indices,
    Triangles_V1_0_1_Vertices,
    Triangles_V1_1_0,
    Triangles_V1_1_0_Indices,
    Triangles_V1_1_0_Vertices,
    Triangles_V1_2_0,
    Triangles_V1_2_0_Indices,
    Triangles_V1_2_0_Vertices,
)
from .unstructured_grid_geometry import (
    UnstructuredGridGeometry_V1_0_1,
    UnstructuredGridGeometry_V1_0_1_Cells,
    UnstructuredGridGeometry_V1_0_1_Vertices,
    UnstructuredGridGeometry_V1_1_0,
    UnstructuredGridGeometry_V1_1_0_Cells,
    UnstructuredGridGeometry_V1_1_0_Vertices,
    UnstructuredGridGeometry_V1_2_0,
    UnstructuredGridGeometry_V1_2_0_Cells,
    UnstructuredGridGeometry_V1_2_0_Vertices,
)
from .variogram_cubic_structure import VariogramCubicStructure_V1_0_1, VariogramCubicStructure_V1_1_0
from .variogram_exponential_structure import VariogramExponentialStructure_V1_0_1, VariogramExponentialStructure_V1_1_0
from .variogram_gaussian_structure import VariogramGaussianStructure_V1_0_1, VariogramGaussianStructure_V1_1_0
from .variogram_generalisedcauchy_structure import (
    VariogramGeneralisedcauchyStructure_V1_0_1,
    VariogramGeneralisedcauchyStructure_V1_1_0,
)
from .variogram_linear_structure import VariogramLinearStructure_V1_0_1, VariogramLinearStructure_V1_1_0
from .variogram_spherical_structure import VariogramSphericalStructure_V1_0_1, VariogramSphericalStructure_V1_1_0
from .variogram_spheroidal_structure import VariogramSpheroidalStructure_V1_0_1, VariogramSpheroidalStructure_V1_1_0
from .vector_attribute import VectorAttribute_V1_0_0
from .vertices_2d import Vertices2D_V1_0_1
from .vertices_3d import Vertices3D_V1_0_1

components_schema_lookup = {
    "/components/attribute-description/1.0.1/attribute-description.schema.json": AttributeDescription_V1_0_1,
    "/components/attribute-list-property/1.0.1/attribute-list-property.schema.json": AttributeListProperty_V1_0_1,
    "/components/attribute-list-property/1.1.0/attribute-list-property.schema.json": AttributeListProperty_V1_1_0,
    "/components/attribute-list-property/1.2.0/attribute-list-property.schema.json": AttributeListProperty_V1_2_0,
    "/components/base-attribute/1.0.0/base-attribute.schema.json": BaseAttribute_V1_0_0,
    "/components/base-category-attribute/1.0.0/base-category-attribute.schema.json": BaseCategoryAttribute_V1_0_0,
    "/components/base-continuous-attribute/1.0.0/base-continuous-attribute.schema.json": BaseContinuousAttribute_V1_0_0,
    "/components/base-object-properties/1.0.1/base-object-properties.schema.json": BaseObjectProperties_V1_0_1,
    "/components/base-object-properties/1.1.0/base-object-properties.schema.json": BaseObjectProperties_V1_1_0,
    "/components/base-spatial-data-properties/1.0.1/base-spatial-data-properties.schema.json": BaseSpatialDataProperties_V1_0_1,
    "/components/base-spatial-data-properties/1.1.0/base-spatial-data-properties.schema.json": BaseSpatialDataProperties_V1_1_0,
    "/components/block-model-attribute/1.0.0/block-model-attribute.schema.json": BlockModelAttribute_V1_0_0,
    "/components/block-model-category-attribute/1.0.0/block-model-category-attribute.schema.json": BlockModelCategoryAttribute_V1_0_0,
    "/components/block-model-flexible-structure/1.0.0/block-model-flexible-structure.schema.json": BlockModelFlexibleStructure_V1_0_0,
    "/components/block-model-fully-subblocked-structure/1.0.0/block-model-fully-subblocked-structure.schema.json": BlockModelFullySubblockedStructure_V1_0_0,
    "/components/block-model-regular-structure/1.0.0/block-model-regular-structure.schema.json": BlockModelRegularStructure_V1_0_0,
    "/components/block-model-variable-octree-structure/1.0.0/block-model-variable-octree-structure.schema.json": BlockModelVariableOctreeStructure_V1_0_0,
    "/components/bool-attribute/1.0.1/bool-attribute.schema.json": BoolAttribute_V1_0_1,
    "/components/bool-attribute/1.1.0/bool-attribute.schema.json": BoolAttribute_V1_1_0,
    "/components/bool-time-series/1.0.1/bool-time-series.schema.json": BoolTimeSeries_V1_0_1,
    "/components/bool-time-series/1.1.0/bool-time-series.schema.json": BoolTimeSeries_V1_1_0,
    "/components/bounding-box/1.0.1/bounding-box.schema.json": BoundingBox_V1_0_1,
    "/components/brep-container/1.0.1/brep-container.schema.json": BrepContainer_V1_0_1,
    "/components/category-attribute-description/1.0.1/category-attribute-description.schema.json": CategoryAttributeDescription_V1_0_1,
    "/components/category-attribute/1.0.1/category-attribute.schema.json": CategoryAttribute_V1_0_1,
    "/components/category-attribute/1.1.0/category-attribute.schema.json": CategoryAttribute_V1_1_0,
    "/components/category-data/1.0.1/category-data.schema.json": CategoryData_V1_0_1,
    "/components/category-ensemble/1.0.1/category-ensemble.schema.json": CategoryEnsemble_V1_0_1,
    "/components/category-ensemble/1.1.0/category-ensemble.schema.json": CategoryEnsemble_V1_1_0,
    "/components/category-time-series/1.0.1/category-time-series.schema.json": CategoryTimeSeries_V1_0_1,
    "/components/category-time-series/1.1.0/category-time-series.schema.json": CategoryTimeSeries_V1_1_0,
    "/components/channel-attribute/1.0.1/channel-attribute.schema.json": ChannelAttribute_V1_0_1,
    "/components/channel-attribute/1.1.0/channel-attribute.schema.json": ChannelAttribute_V1_1_0,
    "/components/color-attribute/1.0.0/color-attribute.schema.json": ColorAttribute_V1_0_0,
    "/components/color-attribute/1.1.0/color-attribute.schema.json": ColorAttribute_V1_1_0,
    "/components/continuous-attribute/1.0.1/continuous-attribute.schema.json": ContinuousAttribute_V1_0_1,
    "/components/continuous-attribute/1.1.0/continuous-attribute.schema.json": ContinuousAttribute_V1_1_0,
    "/components/continuous-ensemble/1.0.1/continuous-ensemble.schema.json": ContinuousEnsemble_V1_0_1,
    "/components/continuous-ensemble/1.1.0/continuous-ensemble.schema.json": ContinuousEnsemble_V1_1_0,
    "/components/continuous-time-series/1.0.1/continuous-time-series.schema.json": ContinuousTimeSeries_V1_0_1,
    "/components/continuous-time-series/1.1.0/continuous-time-series.schema.json": ContinuousTimeSeries_V1_1_0,
    "/components/crs/1.0.1/crs.schema.json": Crs_V1_0_1,
    "/components/cumulative-distribution-function/1.0.1/cumulative-distribution-function.schema.json": CumulativeDistributionFunction_V1_0_1,
    "/components/data-table/1.0.1/data-table.schema.json": DataTable_V1_0_1,
    "/components/data-table/1.1.0/data-table.schema.json": DataTable_V1_1_0,
    "/components/data-table/1.2.0/data-table.schema.json": DataTable_V1_2_0,
    "/components/date-time-attribute/1.0.1/date-time-attribute.schema.json": DateTimeAttribute_V1_0_1,
    "/components/date-time-attribute/1.1.0/date-time-attribute.schema.json": DateTimeAttribute_V1_1_0,
    "/components/desurvey-method/1.0.0/desurvey-method.schema.json": DesurveyMethod_V1_0_0,
    "/components/distance-table/1.0.1/distance-table.schema.json": DistanceTable_V1_0_1,
    "/components/distance-table/1.1.0/distance-table.schema.json": DistanceTable_V1_1_0,
    "/components/distance-table/1.2.0/distance-table.schema.json": DistanceTable_V1_2_0,
    "/components/downhole-attributes/1.0.0/downhole-attributes.schema.json": DownholeAttributes_V1_0_0,
    "/components/downhole-direction-vector/1.0.0/downhole-direction-vector.schema.json": DownholeDirectionVector_V1_0_0,
    "/components/ellipsoid/1.0.1/ellipsoid.schema.json": Ellipsoid_V1_0_1,
    "/components/ellipsoid/1.1.0/ellipsoid.schema.json": Ellipsoid_V1_1_0,
    "/components/ellipsoids/1.0.1/ellipsoids.schema.json": Ellipsoids_V1_0_1,
    "/components/embedded-line-geometry/1.0.0/embedded-line-geometry.schema.json": EmbeddedLineGeometry_V1_0_0,
    "/components/embedded-mesh-object/1.0.0/embedded-mesh-object.schema.json": EmbeddedMeshObject_V1_0_0,
    "/components/embedded-polyline-object/1.0.0/embedded-polyline-object.schema.json": EmbeddedPolylineObject_V1_0_0,
    "/components/embedded-triangulated-mesh/1.0.1/embedded-triangulated-mesh.schema.json": EmbeddedTriangulatedMesh_V1_0_1,
    "/components/embedded-triangulated-mesh/1.1.0/embedded-triangulated-mesh.schema.json": EmbeddedTriangulatedMesh_V1_1_0,
    "/components/embedded-triangulated-mesh/2.0.0/embedded-triangulated-mesh.schema.json": EmbeddedTriangulatedMesh_V2_0_0,
    "/components/embedded-triangulated-mesh/2.1.0/embedded-triangulated-mesh.schema.json": EmbeddedTriangulatedMesh_V2_1_0,
    "/components/frequency-domain-electromagnetic-channel/1.0.0/frequency-domain-electromagnetic-channel.schema.json": FrequencyDomainElectromagneticChannel_V1_0_0,
    "/components/from-to/1.0.1/from-to.schema.json": FromTo_V1_0_1,
    "/components/geometry-composite/1.0.1/geometry-composite.schema.json": GeometryComposite_V1_0_1,
    "/components/geometry-part/1.0.1/geometry-part.schema.json": GeometryPart_V1_0_1,
    "/components/hexahedrons/1.0.1/hexahedrons.schema.json": Hexahedrons_V1_0_1,
    "/components/hexahedrons/1.1.0/hexahedrons.schema.json": Hexahedrons_V1_1_0,
    "/components/hexahedrons/1.2.0/hexahedrons.schema.json": Hexahedrons_V1_2_0,
    "/components/hole-chunks/1.0.0/hole-chunks.schema.json": HoleChunks_V1_0_0,
    "/components/hole-collars/1.0.0/hole-collars.schema.json": HoleCollars_V1_0_0,
    "/components/indices-attribute/1.0.1/indices-attribute.schema.json": IndicesAttribute_V1_0_1,
    "/components/indices-attribute/1.1.0/indices-attribute.schema.json": IndicesAttribute_V1_1_0,
    "/components/integer-attribute/1.0.1/integer-attribute.schema.json": IntegerAttribute_V1_0_1,
    "/components/integer-attribute/1.1.0/integer-attribute.schema.json": IntegerAttribute_V1_1_0,
    "/components/interval-table/1.0.1/interval-table.schema.json": IntervalTable_V1_0_1,
    "/components/interval-table/1.1.0/interval-table.schema.json": IntervalTable_V1_1_0,
    "/components/interval-table/1.2.0/interval-table.schema.json": IntervalTable_V1_2_0,
    "/components/intervals/1.0.1/intervals.schema.json": Intervals_V1_0_1,
    "/components/lengths/1.0.1/lengths.schema.json": Lengths_V1_0_1,
    "/components/lineage/1.0.0/lineage.schema.json": Lineage_V1_0_0,
    "/components/lineation-data/1.0.1/lineation-data.schema.json": LineationData_V1_0_1,
    "/components/lines-2d-indices/1.0.1/lines-2d-indices.schema.json": Lines2DIndices_V1_0_1,
    "/components/lines-3d-indices/1.0.1/lines-3d-indices.schema.json": Lines3DIndices_V1_0_1,
    "/components/locations/1.0.1/locations.schema.json": Locations_V1_0_1,
    "/components/material/1.0.1/material.schema.json": Material_V1_0_1,
    "/components/mesh-quality/1.0.1/mesh-quality.schema.json": MeshQuality_V1_0_1,
    "/components/nan-categorical/1.0.1/nan-categorical.schema.json": NanCategorical_V1_0_1,
    "/components/nan-continuous/1.0.1/nan-continuous.schema.json": NanContinuous_V1_0_1,
    "/components/one-of-attribute/1.0.1/one-of-attribute.schema.json": OneOfAttribute_V1_0_1,
    "/components/one-of-attribute/1.1.0/one-of-attribute.schema.json": OneOfAttribute_V1_1_0,
    "/components/one-of-attribute/1.2.0/one-of-attribute.schema.json": OneOfAttribute_V1_2_0,
    "/components/planar-data/1.0.1/planar-data.schema.json": PlanarData_V1_0_1,
    "/components/polyline-2d/1.0.1/polyline-2d.schema.json": Polyline2D_V1_0_1,
    "/components/polyline-3d/1.0.1/polyline-3d.schema.json": Polyline3D_V1_0_1,
    "/components/quadrilaterals/1.0.1/quadrilaterals.schema.json": Quadrilaterals_V1_0_1,
    "/components/quadrilaterals/1.1.0/quadrilaterals.schema.json": Quadrilaterals_V1_1_0,
    "/components/quadrilaterals/1.2.0/quadrilaterals.schema.json": Quadrilaterals_V1_2_0,
    "/components/relative-lineation-data-table/1.0.1/relative-lineation-data-table.schema.json": RelativeLineationDataTable_V1_0_1,
    "/components/relative-lineation-data-table/1.1.0/relative-lineation-data-table.schema.json": RelativeLineationDataTable_V1_1_0,
    "/components/relative-lineation-data-table/1.2.0/relative-lineation-data-table.schema.json": RelativeLineationDataTable_V1_2_0,
    "/components/relative-planar-data-table/1.0.1/relative-planar-data-table.schema.json": RelativePlanarDataTable_V1_0_1,
    "/components/relative-planar-data-table/1.1.0/relative-planar-data-table.schema.json": RelativePlanarDataTable_V1_1_0,
    "/components/relative-planar-data-table/1.2.0/relative-planar-data-table.schema.json": RelativePlanarDataTable_V1_2_0,
    "/components/resistivity-ip-dcip-survey-properties/1.0.0/resistivity-ip-dcip-survey-properties.schema.json": ResistivityIpDcipSurveyProperties_V1_0_0,
    "/components/resistivity-ip-line/1.1.0/resistivity-ip-line.schema.json": ResistivityIpLine_V1_1_0,
    "/components/resistivity-ip-phaseip-survey-properties/1.0.0/resistivity-ip-phaseip-survey-properties.schema.json": ResistivityIpPhaseipSurveyProperties_V1_0_0,
    "/components/resistivity-ip-pldp-configuration-properties/1.0.0/resistivity-ip-pldp-configuration-properties.schema.json": ResistivityIpPldpConfigurationProperties_V1_0_0,
    "/components/resistivity-ip-plpl-configuration-properties/1.0.0/resistivity-ip-plpl-configuration-properties.schema.json": ResistivityIpPlplConfigurationProperties_V1_0_0,
    "/components/resistivity-ip-sip-survey-properties/1.0.0/resistivity-ip-sip-survey-properties.schema.json": ResistivityIpSipSurveyProperties_V1_0_0,
    "/components/rotation/1.0.1/rotation.schema.json": Rotation_V1_0_1,
    "/components/rotation/1.1.0/rotation.schema.json": Rotation_V1_1_0,
    "/components/segments/1.0.1/segments.schema.json": Segments_V1_0_1,
    "/components/segments/1.1.0/segments.schema.json": Segments_V1_1_0,
    "/components/segments/1.2.0/segments.schema.json": Segments_V1_2_0,
    "/components/string-attribute/1.0.1/string-attribute.schema.json": StringAttribute_V1_0_1,
    "/components/string-attribute/1.1.0/string-attribute.schema.json": StringAttribute_V1_1_0,
    "/components/surface-mesh/1.0.1/surface-mesh.schema.json": SurfaceMesh_V1_0_1,
    "/components/survey-line/1.0.1/survey-line.schema.json": SurveyLine_V1_0_1,
    "/components/survey-line/1.1.0/survey-line.schema.json": SurveyLine_V1_1_0,
    "/components/tetrahedra/1.0.1/tetrahedra.schema.json": Tetrahedra_V1_0_1,
    "/components/tetrahedra/1.1.0/tetrahedra.schema.json": Tetrahedra_V1_1_0,
    "/components/tetrahedra/1.2.0/tetrahedra.schema.json": Tetrahedra_V1_2_0,
    "/components/time-domain-electromagnetic-channel/1.0.0/time-domain-electromagnetic-channel.schema.json": TimeDomainElectromagneticChannel_V1_0_0,
    "/components/time-step-attribute/1.0.1/time-step-attribute.schema.json": TimeStepAttribute_V1_0_1,
    "/components/time-step-attribute/1.1.0/time-step-attribute.schema.json": TimeStepAttribute_V1_1_0,
    "/components/time-step-continuous-attribute/1.0.1/time-step-continuous-attribute.schema.json": TimeStepContinuousAttribute_V1_0_1,
    "/components/time-step-continuous-attribute/1.1.0/time-step-continuous-attribute.schema.json": TimeStepContinuousAttribute_V1_1_0,
    "/components/time-step-date-time-attribute/1.0.1/time-step-date-time-attribute.schema.json": TimeStepDateTimeAttribute_V1_0_1,
    "/components/time-step-date-time-attribute/1.1.0/time-step-date-time-attribute.schema.json": TimeStepDateTimeAttribute_V1_1_0,
    "/components/triangles/1.0.1/triangles.schema.json": Triangles_V1_0_1,
    "/components/triangles/1.1.0/triangles.schema.json": Triangles_V1_1_0,
    "/components/triangles/1.2.0/triangles.schema.json": Triangles_V1_2_0,
    "/components/unstructured-grid-geometry/1.0.1/unstructured-grid-geometry.schema.json": UnstructuredGridGeometry_V1_0_1,
    "/components/unstructured-grid-geometry/1.1.0/unstructured-grid-geometry.schema.json": UnstructuredGridGeometry_V1_1_0,
    "/components/unstructured-grid-geometry/1.2.0/unstructured-grid-geometry.schema.json": UnstructuredGridGeometry_V1_2_0,
    "/components/variogram-cubic-structure/1.0.1/variogram-cubic-structure.schema.json": VariogramCubicStructure_V1_0_1,
    "/components/variogram-cubic-structure/1.1.0/variogram-cubic-structure.schema.json": VariogramCubicStructure_V1_1_0,
    "/components/variogram-exponential-structure/1.0.1/variogram-exponential-structure.schema.json": VariogramExponentialStructure_V1_0_1,
    "/components/variogram-exponential-structure/1.1.0/variogram-exponential-structure.schema.json": VariogramExponentialStructure_V1_1_0,
    "/components/variogram-gaussian-structure/1.0.1/variogram-gaussian-structure.schema.json": VariogramGaussianStructure_V1_0_1,
    "/components/variogram-gaussian-structure/1.1.0/variogram-gaussian-structure.schema.json": VariogramGaussianStructure_V1_1_0,
    "/components/variogram-generalisedcauchy-structure/1.0.1/variogram-generalisedcauchy-structure.schema.json": VariogramGeneralisedcauchyStructure_V1_0_1,
    "/components/variogram-generalisedcauchy-structure/1.1.0/variogram-generalisedcauchy-structure.schema.json": VariogramGeneralisedcauchyStructure_V1_1_0,
    "/components/variogram-linear-structure/1.0.1/variogram-linear-structure.schema.json": VariogramLinearStructure_V1_0_1,
    "/components/variogram-linear-structure/1.1.0/variogram-linear-structure.schema.json": VariogramLinearStructure_V1_1_0,
    "/components/variogram-spherical-structure/1.0.1/variogram-spherical-structure.schema.json": VariogramSphericalStructure_V1_0_1,
    "/components/variogram-spherical-structure/1.1.0/variogram-spherical-structure.schema.json": VariogramSphericalStructure_V1_1_0,
    "/components/variogram-spheroidal-structure/1.0.1/variogram-spheroidal-structure.schema.json": VariogramSpheroidalStructure_V1_0_1,
    "/components/variogram-spheroidal-structure/1.1.0/variogram-spheroidal-structure.schema.json": VariogramSpheroidalStructure_V1_1_0,
    "/components/vector-attribute/1.0.0/vector-attribute.schema.json": VectorAttribute_V1_0_0,
    "/components/vertices-2d/1.0.1/vertices-2d.schema.json": Vertices2D_V1_0_1,
    "/components/vertices-3d/1.0.1/vertices-3d.schema.json": Vertices3D_V1_0_1,
}
