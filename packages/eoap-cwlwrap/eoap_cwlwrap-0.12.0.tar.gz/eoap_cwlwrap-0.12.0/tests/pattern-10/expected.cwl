cwlVersion: v1.2
$graph:
- id: main
  class: Workflow
  label: Workflow pattern-10 orchestrator
  doc: This Workflow is used to orchestrate the Workflow pattern-10
  inputs:
  - id: aoi
    label: area of interest - pattern-10/aoi
    doc: area of interest as a bounding box - This parameter is derived from 
      pattern-10/aoi
    default: -118.985,38.432,-118.183,38.938
    type: string
  - id: epsg
    label: EPSG code - pattern-10/epsg
    doc: EPSG code - This parameter is derived from pattern-10/epsg
    default: EPSG:4326
    type: string
  - id: indexes
    label: indexes - pattern-10/indexes
    doc: indexes to compute - This parameter is derived from pattern-10/indexes
    default:
    - ndvi
    - ndwi
    type:
      name: _:b02493da-e5c1-448f-a4b2-f6fbbb8646e0
      items: string
      type: array
  - id: another_input
    label: Another Input - my-asthonishing-stage-in-directory/another_input
    doc: An additional input for demonstration purposes - This parameter is 
      derived from my-asthonishing-stage-in-directory/another_input
    type: string
  - id: items
    label: Landsat-8/9 acquisition reference - pattern-10/items
    doc: Landsat-8/9 acquisition reference - This parameter is derived from 
      pattern-10/items
    type:
      name: _:18e253a5-4b99-4327-b3d4-c3be10fcc444
      items: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
      type: array
  - id: s3_bucket
    label: my-super-stage-out/s3_bucket
    doc: 'This parameter is derived from: my-super-stage-out/s3_bucket'
    type: string
  - id: sub_path
    label: my-super-stage-out/sub_path
    doc: 'This parameter is derived from: my-super-stage-out/sub_path'
    type: string
  - id: aws_access_key_id
    label: my-super-stage-out/aws_access_key_id
    doc: 'This parameter is derived from: my-super-stage-out/aws_access_key_id'
    type: string
  - id: aws_secret_access_key
    label: my-super-stage-out/aws_secret_access_key
    doc: 'This parameter is derived from: my-super-stage-out/aws_secret_access_key'
    type: string
  - id: region_name
    label: my-super-stage-out/region_name
    doc: 'This parameter is derived from: my-super-stage-out/region_name'
    type: string
  - id: endpoint_url
    label: my-super-stage-out/endpoint_url
    doc: 'This parameter is derived from: my-super-stage-out/endpoint_url'
    type: string
  outputs:
  - id: vegetation_indexes
    label: Vegetation indexes
    doc: Vegetation indexes from Landsat-8/9 acquisitions
    outputSource:
    - stage_out_0/s3_catalog_output
    type:
      name: _:6dbadb72-4251-4c94-97ea-81fa2fc3e678
      items: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
      type: array
  requirements:
  - class: SubworkflowFeatureRequirement
  - class: SchemaDefRequirement
    types:
    - $import: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml
  - class: ScatterFeatureRequirement
  steps:
  - id: directory_stage_in_0
    in:
    - id: reference
      source: items
    - id: another_input
      source: another_input
    out:
    - staged
    run: '#my-asthonishing-stage-in-directory'
    scatter: reference
    scatterMethod: dotproduct
  - id: app
    in:
    - id: aoi
      source: aoi
    - id: epsg
      source: epsg
    - id: indexes
      source: indexes
    - id: items
      source: directory_stage_in_0/staged
    out:
    - vegetation_indexes
    run: '#pattern-10'
  - id: stage_out_0
    in:
    - id: s3_bucket
      source: s3_bucket
    - id: sub_path
      source: sub_path
    - id: aws_access_key_id
      source: aws_access_key_id
    - id: aws_secret_access_key
      source: aws_secret_access_key
    - id: region_name
      source: region_name
    - id: endpoint_url
      source: endpoint_url
    - id: stac_catalog
      source: app/vegetation_indexes
    out:
    - s3_catalog_output
    run: '#my-super-stage-out'
    scatter: stac_catalog
    scatterMethod: dotproduct
- http://commonwl.org/cwltool#original_cwlVersion: v1.2
  id: my-asthonishing-stage-in-directory
  class: CommandLineTool
  inputs:
  - id: reference
    label: STAC Item URL
    doc: A STAC Item to stage
    type: 
      https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
  - id: another_input
    label: Another Input
    doc: An additional input for demonstration purposes
    type: string
  outputs:
  - id: staged
    type: Directory
    outputBinding:
      glob: .
  requirements:
  - class: SchemaDefRequirement
    types:
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Date
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Date/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Duration
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Duration/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Email
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Email/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Hostname
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Hostname/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNEmail
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNEmail/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNHostname
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNHostname/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv4
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv4/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv6
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv6/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRI
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRI/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRIReference
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRIReference/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#JsonPointer
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#JsonPointer/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Password
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Password/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#RelativeJsonPointer
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#RelativeJsonPointer/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#UUID
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#UUID/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URIReference
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URIReference/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URITemplate
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URITemplate/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Time
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Time/value
        type: string
      type: record
  - class: DockerRequirement
    dockerPull: ghcr.io/eoap/mastering-app-package/stage:1.0.0
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
    - entryname: stage.py
      entry: |-
        import pystac
        import stac_asset
        import asyncio
        import os
        import sys

        config = stac_asset.Config(warn=True)

        async def main(href: str):
            
            item = pystac.read_file(href)
            
            os.makedirs(item.id, exist_ok=True)
            cwd = os.getcwd()
            
            os.chdir(item.id)
            item = await stac_asset.download_item(item=item, directory=".", config=config)
            os.chdir(cwd)
            
            cat = pystac.Catalog(
                id="catalog",
                description=f"catalog with staged {item.id}",
                title=f"catalog with staged {item.id}",
            )
            cat.add_item(item)
            
            cat.normalize_hrefs("./")
            cat.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

            return cat

        href = sys.argv[1]
        empty_arg = sys.argv[2]

        cat = asyncio.run(main(href))
  cwlVersion: v1.2
  baseCommand:
  - python
  - stage.py
  arguments:
  - $( inputs.reference.value )
  - $( inputs.another_input )
- id: pattern-10
  class: Workflow
  label: NDVI and NDWI vegetation indexes
  doc: NDVI and NDWI vegetation indexes from Landsat-8/9 acquisitions
  inputs:
  - id: aoi
    label: area of interest
    doc: area of interest as a bounding box
    default: -118.985,38.432,-118.183,38.938
    type: string
  - id: epsg
    label: EPSG code
    doc: EPSG code
    default: EPSG:4326
    type: string
  - id: indexes
    label: indexes
    doc: indexes to compute
    default:
    - ndvi
    - ndwi
    type:
      name: _:b02493da-e5c1-448f-a4b2-f6fbbb8646e0
      items: string
      type: array
  - id: items
    label: Landsat-8/9 acquisition reference
    doc: Landsat-8/9 acquisition reference
    type:
      name: _:54801c05-75fd-4151-a35d-4e608e1d3f1e
      items: Directory
      type: array
  outputs:
  - id: vegetation_indexes
    label: Vegetation indexes
    doc: Vegetation indexes from Landsat-8/9 acquisitions
    outputSource:
    - flatten/flat
    type:
      name: _:cbe0dbb6-a571-4382-88e9-c30c2ba65674
      items: Directory
      type: array
  requirements:
  - class: SubworkflowFeatureRequirement
  - class: ScatterFeatureRequirement
  cwlVersion: v1.2
  steps:
  - id: subworkflow
    in:
    - id: item
      source: items
    - id: aoi
      source: aoi
    - id: epsg
      source: epsg
    - id: indexes
      source: indexes
    out:
    - vegetation_indexes
    run: '#vegetation_indexes'
    scatter:
    - subworkflow/item
    scatterMethod: dotproduct
  - id: flatten
    in:
    - id: nested
      source: subworkflow/vegetation_indexes
    out:
    - flat
    run: '#flatten_array'
  $namespaces: &id001
    s: https://schema.org/
- http://commonwl.org/cwltool#original_cwlVersion: v1.2
  id: my-super-stage-out
  class: CommandLineTool
  doc: Stage-out the results to S3
  inputs:
  - id: s3_bucket
    type: string
  - id: sub_path
    type: string
  - id: aws_access_key_id
    type: string
  - id: aws_secret_access_key
    type: string
  - id: region_name
    type: string
  - id: endpoint_url
    type: string
  - id: stac_catalog
    label: STAC Catalog folder
    doc: The folder containing the STAC catalog to stage out
    type: Directory
  outputs:
  - id: s3_catalog_output
    type: 
      https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
    outputBinding:
      loadContents: true
      glob: catalog-uri.txt
      outputEval: |
        ${ 
          return { "value": self[0].contents, "type": "https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI" };
        }
  requirements:
  - class: SchemaDefRequirement
    types:
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Date
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Date/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#DateTime/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Duration
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Duration/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Email
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Email/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Hostname
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Hostname/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNEmail
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNEmail/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNHostname
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IDNHostname/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv4
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv4/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv6
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IPv6/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRI
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRI/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRIReference
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#IRIReference/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#JsonPointer
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#JsonPointer/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Password
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Password/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#RelativeJsonPointer
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#RelativeJsonPointer/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#UUID
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#UUID/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URI/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URIReference
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URIReference/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URITemplate
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#URITemplate/value
        type: string
      type: record
    - name: 
        https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Time
      fields:
      - name: 
          https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml#Time/value
        type: string
      type: record
  - class: DockerRequirement
    dockerPull: ghcr.io/eoap/mastering-app-package/stage:1.0.0
  - class: InlineJavascriptRequirement
  - class: EnvVarRequirement
    envDef:
    - envName: aws_access_key_id
      envValue: $( inputs.aws_access_key_id )
    - envName: aws_secret_access_key
      envValue: $( inputs.aws_secret_access_key )
    - envName: aws_region_name
      envValue: $( inputs.region_name )
    - envName: aws_endpoint_url
      envValue: $( inputs.endpoint_url )
  - class: ResourceRequirement
  - class: InitialWorkDirRequirement
    listing:
    - entryname: stage.py
      entry: |-
        import os
        import sys
        import pystac
        import botocore
        import boto3
        import shutil
        from pystac.stac_io import DefaultStacIO, StacIO
        from urllib.parse import urlparse

        cat_url = sys.argv[1]
        bucket = sys.argv[2]
        subfolder = sys.argv[3]

        aws_access_key_id = os.environ["aws_access_key_id"]
        aws_secret_access_key = os.environ["aws_secret_access_key"]
        region_name = os.environ["aws_region_name"]
        endpoint_url = os.environ["aws_endpoint_url"]

        shutil.copytree(cat_url, "/tmp/catalog")
        cat = pystac.read_file(os.path.join("/tmp/catalog", "catalog.json"))

        class CustomStacIO(DefaultStacIO):
            """Custom STAC IO class that uses boto3 to read from S3."""

            def __init__(self):
                self.session = botocore.session.Session()
                self.s3_client = self.session.create_client(
                    service_name="s3",
                    use_ssl=True,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    endpoint_url=endpoint_url,
                    region_name=region_name,
                )

            def write_text(self, dest, txt, *args, **kwargs):
                parsed = urlparse(dest)
                if parsed.scheme == "s3":
                    self.s3_client.put_object(
                        Body=txt.encode("UTF-8"),
                        Bucket=parsed.netloc,
                        Key=parsed.path[1:],
                        ContentType="application/geo+json",
                    )
                else:
                    super().write_text(dest, txt, *args, **kwargs)


        client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )

        StacIO.set_default(CustomStacIO)

        for item in cat.get_items():
            for key, asset in item.get_assets().items():
                s3_path = os.path.normpath(
                    os.path.join(os.path.join(subfolder, item.id, asset.href))
                )
                print(f"upload {asset.href} to s3://{bucket}/{s3_path}",file=sys.stderr)
                client.upload_file(
                    asset.get_absolute_href(),
                    bucket,
                    s3_path,
                )
                asset.href = f"s3://{bucket}/{s3_path}"
                item.add_asset(key, asset)

        cat.normalize_hrefs(f"s3://{bucket}/{subfolder}")

        for item in cat.get_items():
            # upload item to S3
            print(f"upload {item.id} to s3://{bucket}/{subfolder}", file=sys.stderr)
            pystac.write_file(item, item.get_self_href())

        # upload catalog to S3
        print(f"upload catalog.json to s3://{bucket}/{subfolder}", file=sys.stderr)
        pystac.write_file(cat, cat.get_self_href())

        print(f"s3://{bucket}/{subfolder}/catalog.json", end="", file=sys.stdout)
  cwlVersion: v1.2
  baseCommand:
  - python
  - stage.py
  arguments:
  - $( inputs.stac_catalog.path )
  - $( inputs.s3_bucket )
  - ${ var firstPart = (Math.random() * 46656) | 0; var secondPart = 
    (Math.random() * 46656) | 0; firstPart = ("000" + 
    firstPart.toString(36)).slice(-3); secondPart = ("000" + 
    secondPart.toString(36)).slice(-3); return inputs.sub_path + "-" + firstPart
    + secondPart; }
  stdout: catalog-uri.txt
- id: vegetation_indexes
  class: Workflow
  label: NDVI and NDWI vegetation indexes
  doc: NDVI and NDWI vegetation indexes
  inputs:
  - id: aoi
    label: area of interest
    doc: area of interest as a bounding box
    type: string
  - id: epsg
    label: EPSG code
    doc: EPSG code
    default: EPSG:4326
    type: string
  - id: indexes
    label: indexes
    doc: indexes to compute
    default:
    - ndvi
    - ndwi
    type:
      name: _:133f0ece-00b8-4825-8523-dad8d4e66aab
      items: string
      type: array
  - id: item
    label: STAC item reference
    doc: Reference to a STAC item
    type: Directory
  outputs:
  - id: vegetation_indexes
    label: Vegetation indexes
    doc: Vegetation indexes
    outputSource:
    - step/vegetation_index
    type:
      name: _:e784676f-b0b8-4e90-91f6-17bcfe3b0d78
      items: Directory
      type: array
  requirements:
  - class: ScatterFeatureRequirement
  cwlVersion: v1.2
  steps:
  - id: step
    in:
    - id: item
      source: item
    - id: aoi
      source: aoi
    - id: epsg
      source: epsg
    - id: index
      source: indexes
    out:
    - vegetation_index
    run: '#clt'
    scatter: step/index
    scatterMethod: dotproduct
  $namespaces: *id001
- id: clt
  class: CommandLineTool
  inputs:
  - id: item
    type: Directory
    inputBinding:
      prefix: --input-item
  - id: aoi
    type: string
    inputBinding:
      prefix: --aoi
  - id: epsg
    type: string
    inputBinding:
      prefix: --epsg
  - id: index
    type: string
    inputBinding:
      prefix: --vegetation-index
  outputs:
  - id: vegetation_index
    type: Directory
    outputBinding:
      glob: .
  requirements:
  - class: InlineJavascriptRequirement
  - class: EnvVarRequirement
    envDef:
    - envName: PATH
      envValue: $PATH:/app/envs/vegetation-index/bin
  - class: ResourceRequirement
    coresMax: 1
    ramMax: 512
  hints:
  - class: DockerRequirement
    dockerPull: docker.io/library/vegetation-indexes:latest
  cwlVersion: v1.2
  baseCommand:
  - vegetation-index
  arguments:
  - pattern-5
  $namespaces: *id001
- id: flatten_array
  class: ExpressionTool
  label: Flatten Directory[][] → Directory[]
  inputs:
  - id: nested
    type:
      name: _:0151a36f-8fe2-480e-bbad-e7ed9e5e000d
      items:
        name: _:d9de8ef8-5a19-4ddc-82ef-ee3d0ec621e8
        items: Directory
        type: array
      type: array
  outputs:
  - id: flat
    type:
      name: _:eb2c03e1-e739-4455-9f4e-544b5556c415
      items: Directory
      type: array
  requirements:
  - class: InlineJavascriptRequirement
  cwlVersion: v1.2
  expression: |
    ${ return { flat: [].concat(...inputs.nested) }; }
  $namespaces: *id001
