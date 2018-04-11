function graphSet_jsonFileLoad(astr_jsonFileName) {
    // Simply return a graph set read from a json file

    return (function(Graph) {
        d3.json(astr_jsonFileName, Graph);
    })
}

function getGraphDataSets() {

    let l_graph = [
        'chris-1',
        'chris-2',
        'chris-3',
        'chris-4',
        'chris-5'
    ];

    let l_graphFunction = [];

    for (i in l_graph) {
        const funcObj = graphSet_jsonFileLoad(l_graph[i] + '.json');
        funcObj.description = "<em>" + l_graph[i] + "</em> topology";
        funcObj.uid = l_graph[i];
        l_graphFunction.push(funcObj);
    }

    return l_graphFunction;
}