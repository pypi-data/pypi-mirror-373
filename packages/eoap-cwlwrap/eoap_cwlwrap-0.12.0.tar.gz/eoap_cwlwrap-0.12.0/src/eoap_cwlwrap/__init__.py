'''
EOAP CWLWrap is a command-line utility that composes a CWL `Workflow` from a series of `Workflow`/`CommandLineTool` steps, defined according to [Application package patterns based on data stage-in and stage-out behaviors commonly used in EO workflows](https://github.com/eoap/application-package-patterns), and **packs** it into a single self-contained CWL document.

EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
'''

import sys
from .types import (
    Directory_or_File,
    get_assignable_type,
    is_array_type,
    is_directory_compatible_type,
    is_type_assignable_to,
    is_uri_compatible_type,
    is_nullable,
    replace_directory_with_url,
    replace_type_with_url,
    type_to_string,
    URL_SCHEMA,
    validate_directory_stage_in,
    validate_file_stage_in,
    validate_stage_out,
    Workflows
)
from cwl_loader import load_cwl_from_yaml
from cwl_utils.parser.cwl_v1_2 import (
    InlineJavascriptRequirement,
    ProcessRequirement,
    ScatterFeatureRequirement,
    SchemaDefRequirement,
    SubworkflowFeatureRequirement,
    Workflow,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStep,
    WorkflowStepInput
)
from loguru import logger
from typing import (
    Any,
    Mapping,
    Optional
)
import sys
import time

def _to_workflow_input_parameter(
    source: str,
    parameter: Any,
    target_type: Optional[Any] = None
) -> WorkflowInputParameter:
    return WorkflowInputParameter(
        type_=target_type if target_type else parameter.type_,
        label=f"{parameter.label} - {source}/{parameter.id}" if parameter.label else f"{source}/{parameter.id}",
        secondaryFiles=parameter.secondaryFiles,
        streamable=parameter.streamable,
        doc=f"{parameter.doc} - This parameter is derived from {source}/{parameter.id}" if parameter.label else f"This parameter is derived from: {source}/{parameter.id}",
        id=parameter.id,
        format=parameter.format,
        loadContents=parameter.loadContents,
        loadListing=parameter.loadListing,
        default=parameter.default,
        inputBinding=parameter.inputBinding,
        extension_fields=parameter.extension_fields,
        loadingOptions=parameter.loadingOptions,
    )

def _add_feature_requirement(
    requirement: ProcessRequirement,
    workflow: Workflow
):
    if any(requirement.class_ == current_requirement.class_ for current_requirement in workflow.requirements):
        return;

    workflow.requirements.append(requirement)

def _build_orchestrator_workflow(
    directory_stage_in: Workflow,
    file_stage_in: Workflow,
    workflow: Workflow,
    stage_out: Workflow
) -> Workflow:
    start_time = time.time()
    logger.info(f"Building the CWL Orchestrator Workflow...")

    imports = { URL_SCHEMA }

    def _ad_import(type_string: str):
        if '#' in type_string:
            imports.add(type_string.split('#')[0])

    orchestrator = Workflow(
        id='main',
        label=f"{workflow.class_} {workflow.id} orchestrator",
        doc=f"This Workflow is used to orchestrate the {workflow.class_} {workflow.id}",
        requirements=[SubworkflowFeatureRequirement()],
        inputs=[],
        outputs=[],
        steps=[]
    )

    main_workflow = [ orchestrator ]

    app = WorkflowStep(
        id='app',
        in_=[],
        out=[],
        run=f"#{workflow.id}"
    )

    # inputs

    logger.info(f"Analyzing {workflow.id} inputs...")

    stage_in_counters = {
        'Directory': 0,
        'File': 0
    }

    stage_in_cwl = {
        'Directory': directory_stage_in,
        'File': file_stage_in
    }

    for input in workflow.inputs:
        type_string = type_to_string(input.type_)
        _ad_import(type_string)

        logger.info(f"* {workflow.id}/{input.id}: {type_string}")

        assignable_type = get_assignable_type(actual=input.type_, expected=Directory_or_File)

        target_type = input.type_

        if assignable_type:
            stage_in = stage_in_cwl[type_to_string(assignable_type)]
            if not stage_in:
                sys.exit(f"  input requires a {type_to_string(assignable_type)} stage-in, that was not specified")

            stage_in_id = f"{type_to_string(assignable_type).lower()}_stage_in_{stage_in_counters[type_to_string(assignable_type)]}"

            logger.info(f"  {type_to_string(assignable_type)} type detected, creating a related '{stage_in_id}'...")

            logger.info(f"  Converting {type_to_string(input.type_)} to URL-compatible type...")

            target_type = replace_type_with_url(source=input.type_, to_be_replaced=Directory_or_File)

            logger.info(f"  {type_to_string(input.type_)} converted to {type_to_string(target_type)}")

            workflow_step = WorkflowStep(
                id=stage_in_id,
                in_=[],
                out=list(map(lambda out: out.id, stage_in.outputs)),
                run=f"#{stage_in.id}"
            )

            orchestrator.steps.append(workflow_step)

            for stage_in_input in stage_in.inputs:
                workflow_step.in_.append(
                    WorkflowStepInput(
                        id=stage_in_input.id,
                        source=input.id if is_uri_compatible_type(stage_in_input.type_) else stage_in_input.id
                    )
                )

                if is_uri_compatible_type(stage_in_input.type_):
                    if is_array_type(input.type_):
                        logger.info(f"  Array detected, 'scatter' required for {stage_in_input.id}:{input.id}")

                        workflow_step.scatter = stage_in_input.id
                        workflow_step.scatterMethod = 'dotproduct'

                        _add_feature_requirement(
                            requirement=ScatterFeatureRequirement(),
                            workflow=orchestrator
                        )

                    if is_nullable(input.type_):
                        logger.info(f"  Nullable detected, 'when' required for {stage_in_input.id}:{input.id}")

                        workflow_step.when = f"$(inputs.{stage_in_input.id} !== null)"

                        _add_feature_requirement(
                            requirement=InlineJavascriptRequirement(),
                            workflow=orchestrator
                        )

            logger.info(f"  Connecting 'app/{input.id}' to '{stage_in_id}' output...")

            app.in_.append(
                WorkflowStepInput(
                    id=input.id,
                    source=f"{stage_in_id}/{next(filter(lambda out: is_type_assignable_to(out.type_, Directory_or_File), stage_in.outputs), None).id}"
                )
            )

            if 0 == stage_in_counters[type_to_string(assignable_type)]:
                main_workflow.append(stage_in)

                orchestrator.inputs.extend(
                    list(
                        map(
                            lambda parameter: _to_workflow_input_parameter(stage_in.id, parameter),
                            list(
                                filter(
                                    lambda workflow_input: not is_uri_compatible_type(workflow_input.type_),
                                    stage_in.inputs
                                )
                            )
                        )
                    )
                )

            stage_in_counters[type_to_string(assignable_type)] += 1
        else:
            app.in_.append(
                WorkflowStepInput(
                    id=input.id,
                    source=input.id
                )
            )

        orchestrator.inputs.append(
            _to_workflow_input_parameter(
                source=workflow.id,
                parameter=input,
                target_type=target_type
            )
        )

    # once all '{type}_stage_in_{index}' are defined, we can now append the 'app' step

    main_workflow.append(workflow)

    orchestrator.steps.append(app)

    # outputs

    logger.info(f"Analyzing {workflow.id} outputs...")

    stage_out_counter = 0
    for output in workflow.outputs:
        type_string = type_to_string(output.type_)
        _ad_import(type_string)
        logger.info(f"* {workflow.id}/{output.id}: {type_string}")

        app.out.append(output.id)

        if is_directory_compatible_type(output.type_):
            logger.info(f"  Directory type detected, creating a related 'stage_out_{stage_out_counter}'...")

            logger.info(f"  Converting {type_to_string(output.type_)} to URL-compatible type...")

            url_type = replace_directory_with_url(output.type_)

            logger.info(f"  {type_to_string(output.type_)} converted to {type_to_string(url_type)}")

            workflow_step = WorkflowStep(
                id=f"stage_out_{stage_out_counter}",
                in_=[],
                out=list(map(lambda out: out.id, stage_out.outputs)),
                run=f"#{stage_out.id}"
            )

            orchestrator.steps.append(workflow_step)

            for stage_out_input in stage_out.inputs:
                workflow_step.in_.append(
                    WorkflowStepInput(
                        id=stage_out_input.id,
                        source=f"app/{output.id}" if is_directory_compatible_type(stage_out_input.type_) else stage_out_input.id,
                    )
                )

                if is_directory_compatible_type(stage_out_input.type_):
                    if is_array_type(url_type):
                        logger.info(f"  Array detected, scatter required for {stage_out_input.id}:app/{output.id}")

                        workflow_step.scatter = stage_out_input.id
                        workflow_step.scatterMethod = 'dotproduct'

                        _add_feature_requirement(
                            requirement=ScatterFeatureRequirement(),
                            workflow=orchestrator
                        )

                    if is_nullable(url_type):
                        logger.info(f"  Nullable detected, 'when' required for {stage_out_input.id}:app/{output.id}")

                        workflow_step.when = f"$(inputs.{stage_out_input.id} !== null)"

                        _add_feature_requirement(
                            requirement=InlineJavascriptRequirement(),
                            workflow=orchestrator
                        )

            logger.info(f"  Connecting 'app/{output.id}' to 'stage_out_{stage_out_counter}' output...")

            orchestrator.outputs.append(
                next(
                    map(
                        lambda mapping_output: WorkflowOutputParameter(
                            id=output.id,
                            type_=url_type,
                            outputSource=[f"stage_out_{stage_out_counter}/{mapping_output.id}"],
                            label=output.label,
                            secondaryFiles=output.secondaryFiles,
                            streamable=output.streamable,
                            doc=output.doc,
                            format=output.format,
                            extension_fields=output.extension_fields,
                            loadingOptions=output.loadingOptions
                        ),
                        filter(
                            lambda stage_out_cwl_output: is_uri_compatible_type(stage_out_cwl_output.type_),
                            stage_out.outputs
                        )
                    ),
                    None
                )
            )

            stage_out_counter += 1
        else:
            orchestrator.outputs.append(
                WorkflowOutputParameter(
                    type_=output.type_,
                    label=f"{output.label} - app/{output.id}" if output.label else f"app/{output.id}",
                    secondaryFiles=output.secondaryFiles,
                    streamable=output.streamable,
                    doc=f"{output.doc} - This output is derived from app/{output.id}" if output.label else f"This output is derived from: app/{output.id}",
                    id=output.id,
                    format=output.format,
                    outputSource=[ f"app/{output.id}" ],
                    linkMerge=output.linkMerge,
                    pickValue=output.pickValue,
                    extension_fields=output.extension_fields,
                    loadingOptions=output.loadingOptions
                )
            )

    if stage_out_counter > 0:
        main_workflow.append(stage_out)

        orchestrator.inputs.extend(
            list(
                map(
                    lambda parameter: _to_workflow_input_parameter(stage_out.id, parameter),
                    list(
                        filter(
                            lambda workflow_input: not is_directory_compatible_type(workflow_input.type_),
                            stage_out.inputs
                        )
                    )
                )
            )
        )

    _add_feature_requirement(
        requirement=SchemaDefRequirement(
            types=list(
                map(
                    lambda import_: { '$import': import_ },
                    imports
                )
            )
        ),
        workflow=orchestrator
    )

    end_time = time.time()
    logger.info(f"Orchestrator Workflow built in {end_time - start_time:.4f} seconds")

    return main_workflow

def _search_workflow(workflow_id: str, workflow: Workflows) -> Workflow:
    if isinstance(workflow, list):
        for wf in workflow:
            if workflow_id in wf.id:
                return wf
    elif workflow_id in workflow.id:
        return wf

    sys.exit(f"Sorry, '{workflow_id}' not found in the workflow input file, only {list(map(lambda wf: wf.id, workflow)) if isinstance(workflow, list) else [workflow.id]} available.")

def wrap(
    workflows: Workflows,
    workflow_id: str,
    stage_out: Workflow,
    directory_stage_in: Optional[Workflow] = None,
    file_stage_in: Optional[Workflow] = None
) -> list[Workflow]:
    '''
    Composes a CWL `Workflow` from a series of `Workflow`/`CommandLineTool` steps, defined according to [Application package patterns based on data stage-in and stage-out behaviors commonly used in EO workflows](https://github.com/eoap/application-package-patterns), and **packs** it into a single self-contained CWL document.

    Args:
        `workflows` (`Workflows`): The CWL document object model (or models, if the CWl is a `$graph`)
        `workflow_id` (`str`): ID of the workflow
        `stage_out` (`Workflow`): The CWL stage-out document object model
        `directory_stage_in` (`Optional[Workflow]`): The CWL stage-in file for `Directory` derived types
        `file_stage_in` (`Optional[Workflow]`): The CWL stage-in file for `File` derived types

    Returns:
        `list[Workflow]`: The composed CWL `$graph`.
    '''
    if directory_stage_in:
        validate_directory_stage_in(directory_stage_in=directory_stage_in)

    if file_stage_in:
        validate_file_stage_in(file_stage_in=file_stage_in)

    workflow = _search_workflow(workflow_id=workflow_id, workflow=workflows)
    validate_stage_out(stage_out=stage_out)

    orchestrator = _build_orchestrator_workflow(
        directory_stage_in=directory_stage_in,
        file_stage_in=file_stage_in,
        workflow=workflow,
        stage_out=stage_out
    )

    if isinstance(workflows, list):
        for wf in workflows:
            if workflow_id not in wf.id:
                orchestrator.append(wf)

    return orchestrator

def wrap_raw(
    workflows: Mapping[str, Any],
    workflow_id: str,
    stage_out: Mapping[str, Any],
    directory_stage_in: Optional[Mapping[str, Any]] = None,
    file_stage_in: Optional[Mapping[str, Any]] = None
)-> list[Workflow]:
    '''
    Composes a CWL `Workflow` from a series of `Workflow`/`CommandLineTool` steps, defined according to [Application package patterns based on data stage-in and stage-out behaviors commonly used in EO workflows](https://github.com/eoap/application-package-patterns), and **packs** it into a single self-contained CWL document.

    Args:
        `workflows` (`Mapping[str, Any]`): The CWL document object model (or models, if the CWl is a `$graph`)
        `workflow_id` (`str`): ID of the workflow
        `stage_out` (`Mapping[str, Any]`): The CWL stage-out document object model
        `directory_stage_in` (`Optional[Mapping[str, Any]]`): The CWL stage-in file for `Directory` derived types
        `file_stage_in` (`Optional[Mapping[str, Any]]`): The CWL stage-in file for `File` derived types

    Returns:
        `list[Workflow]`: The composed CWL `$graph`.
    '''
    return wrap(
        workflows=load_cwl_from_yaml(workflows),
        workflow_id=workflow_id,
        stage_out=load_cwl_from_yaml(stage_out),
        directory_stage_in=load_cwl_from_yaml(directory_stage_in) if directory_stage_in else None,
        file_stage_in=load_cwl_from_yaml(file_stage_in) if file_stage_in else None
    )
