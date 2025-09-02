from rpaworkflow.node import WorkflowNode, MergeWorkflowNode


def or_(*nodes: WorkflowNode):
    return MergeWorkflowNode(
        name=' | '.join([node.name for node in nodes]),
        description=' | '.join([node.description for node in nodes]),
        nodes=list(nodes),
        merge_type='or',
    )


def and_(*nodes: WorkflowNode):
    return MergeWorkflowNode(
        name=' & '.join([node.name for node in nodes]),
        description=' & '.join([node.description for node in nodes]),
        nodes=list(nodes),
        merge_type='and'
    )
