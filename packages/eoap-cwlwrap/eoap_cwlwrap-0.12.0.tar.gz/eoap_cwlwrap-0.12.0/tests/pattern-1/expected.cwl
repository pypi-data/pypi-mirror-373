cwlVersion: v1.2

$graph: 
- class: Workflow
  id: main
  label: Temporary workflow for packing 
  doc: This workflow is used to pack the CWL files

  requirements:
    SubworkflowFeatureRequirement: {}

  inputs: 
    # from pattern-1.cwl
    aoi:
      label: area of interest
      doc: area of interest as a bounding box
      type: string
    epsg:
      label: EPSG code
      doc: EPSG code
      type: string
      default: "EPSG:4326"
    bands:
      label: bands used for the NDWI
      doc: bands used for the NDWI
      type: string[]
      default: ["green", "nir08"]
    
    # trasformation from pattern-1.cwl 
    # Directory -> URL
    item:
      doc: Reference to a STAC item
      label: STAC item reference
      type: string # should be URL

    # from stage-in.cwl
    # nothing (this time)
    another_input: 
      type: string
      doc: An additional input for demonstration purposes
      label: Another Input  

    # from stage-out.cwl
    s3_bucket:
      type: string
    sub_path:
      type: string
    aws_access_key_id:
      type: string
    aws_secret_access_key:
      type: string
    region_name:
      type: string
    endpoint_url:
      type: string

  outputs:
    stac_catalog:
      type: string # should be type URL
      outputSource: 
      - stage_out/s3_catalog_output

  steps:

    stage_in:
      run: stage-in.cwl
      in:
        reference: item
        another_input: another_input
      out:
        - staged

    app:
      run: workflow.cwl
      in:
        item: stage_in/staged
        aoi: aoi
        epsg: epsg
        bands: bands
      out:
        - stac_catalog

    stage_out:
      run: stage-out.cwl
      in:
        s3_bucket: s3_bucket
        sub_path: sub_path
        aws_access_key_id: aws_access_key_id
        aws_secret_access_key: aws_secret_access_key
        region_name: region_name
        endpoint_url: endpoint_url
        stac_catalog: app/stac_catalog
      out:
        - s3_catalog_output
