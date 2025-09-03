
# `Governance Definition Context` with Qualified Name: `GovernanceApproach::New Sustainability Governance Domain`


    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Egeria Report</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #2c3e50; }
            h2 { color: #3498db; }
            pre { background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Governance Definition Report - created at 2025-07-17 20:50</h1>
<pre><code>Governance Definition  found from the search string:  `All`
</code></pre>
<p><a id="334fc1df-692a-4960-bbff-343bf7c486d2"></a></p>
<h1>Governance Definition Name: New Sustainability Governance Domain</h1>
<h2>Type Name</h2>
<p>GovernanceApproach</p>
<h2>Extended Properties</h2>
<p>{'summary': 'Set up a new governance domain for sustainability to educate and drive action.', 'implications': {'typeName': 'array<string>', 'arrayCount': 1, 'arrayValues': {'propertyValueMap': {'0': {'class': 'PrimitiveTypePropertyValue', 'typeName': 'string', 'primitiveTypeCategory': 'OM_PRIMITIVE_TYPE_STRING', 'primitiveValue': 'Individuals in the company will be assigned new responsibilities to drive initiatives.'}}, 'propertyCount': 1, 'propertyNames': ['0'], 'propertiesAsStrings': {'0': 'Individuals in the company will be assigned new responsibilities to drive initiatives.'}}}, 'description': 'The new governance domain would provide a focal point for education, initiatives and awards that improve the sustainability of Coco Pharmaceuticals. particularly where cross-organizational collaboration is required.  It will include a leader, a community of advocates and location leaders to help drive initiatives across the organization'}</p>
<h2>Document Identifier</h2>
<p>GovernanceApproach::New Sustainability Governance Domain</p>
<h2>Title</h2>
<p>New Sustainability Governance Domain</p>
<h2>Scope</h2>
<p>Across Coco Pharmaceuticals</p>
<h2>Domain Identifier</h2>
<p>9</p>
<h2>Importance</h2>
<p>High</p>
<h2>GUID</h2>
<p>334fc1df-692a-4960-bbff-343bf7c486d2</p>
<h2>Mermaid Graph</h2>
<p>
    <!DOCTYPE html>
    <html>
        <head>
          <style type="text/css">
            #mySvgId {
            width: 100%;
            height: 1200px;
            overflow: scroll;
            border: 2px solid #ccc;
            position: relative;
            margin-bottom: 10px;
            }
            svg {
            cursor: grab;
            }
    
          </style>
        </head>
    
        <title>Governance Definition - New Sustainability Governance Domain </title>
        <h3>Governance Definition - New Sustainability Governance Domain </h3>
        GUID : 334fc1df-692a-4960-bbff-343bf7c486d2

    
        <body>
        
          <div id="graphDiv"></div>
          <script src="https://bumbu.me/svg-pan-zoom/dist/svg-pan-zoom.min.js"></script>
          <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    
            mermaid.initialize({startOnLoad: false});
            await mermaid.run({
              querySelector: '.mermaid',
              postRenderCallback: (id) => {
                const container = document.getElementById("diagram-container");
                const svgElement = container.querySelector("svg");
    
                // Initialize Panzoom
                const panzoomInstance = Panzoom(svgElement, {
                  maxScale: 5,
                  minScale: 0.5,
                  step: 0.1,
                });
    
                // Add mouse wheel zoom
                container.addEventListener("wheel", (event) => {
                  panzoomInstance.zoomWithWheel(event);
                });
              }
            });
    
    
            const drawDiagram = async function () {
              const element = document.querySelector('#graphDiv');
             const graphDefinition = `
    flowchart LR
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: doc, label: "*Governance Approach*
**New Sustainability Governance Domain**"}
2@{ shape: text, label: "*Scope*
**Across Coco Pharmaceuticals**"}
3@{ shape: text, label: "*Importance*
**High**"}
2~~~3
4@{ shape: doc, label: "*Governance Strategy*
**Operate Coco Pharmaceuticals in an increasingly sustainable way**"}
4==>|"Governance Response"|1
5@{ shape: doc, label: "*Governance Responsibility*
**Sustainability leadership**"}
1==>|"Governance Implementation"|5
6@{ shape: doc, label: "*Governance Responsibility*
**Sustainability Champion**"}
1==>|"Governance Implementation"|6
7@{ shape: doc, label: "*Governance Responsibility*
**Deliver Sustainability Reporting Capability**"}
1==>|"Governance Implementation"|7
style 1 color:#FFFFFF, fill:#006400, stroke:#000000
style 2 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 3 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 4 color:#FFFFFF, fill:#006400, stroke:#000000
style 5 color:#FFFFFF, fill:#006400, stroke:#000000
style 6 color:#FFFFFF, fill:#006400, stroke:#000000
style 7 color:#FFFFFF, fill:#006400, stroke:#000000`;
              const {svg} = await mermaid.render('mySvgId', graphDefinition);
              element.innerHTML = svg.replace(/( )*max-width:( 0-9\.)*px;/i, '');
    
              var doPan = false;
              var eventsHandler;
              var panZoom;
              var mousepos;
    
              eventsHandler = {
                haltEventListeners: ['mousedown', 'mousemove', 'mouseup']
    
                , mouseDownHandler: function (ev) {
                  if (event.target.className == "[object SVGAnimatedString]") {
                    doPan = true;
                    mousepos = {x: ev.clientX, y: ev.clientY}
                  }
                  ;
                }
    
                , mouseMoveHandler: function (ev) {
                  if (doPan) {
                    panZoom.panBy({x: ev.clientX - mousepos.x, y: ev.clientY - mousepos.y});
                    mousepos = {x: ev.clientX, y: ev.clientY};
                    window.getSelection().removeAllRanges();
                  }
                }
    
                , mouseUpHandler: function (ev) {
                  doPan = false;
                }
    
                , init: function (options) {
                  options.svgElement.addEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.addEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.addEventListener('mouseup', this.mouseUpHandler, false);
                }
    
                , destroy: function (options) {
                  options.svgElement.removeEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.removeEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.removeEventListener('mouseup', this.mouseUpHandler, false);
                }
              }
              panZoom = svgPanZoom('#mySvgId', {
                zoomEnabled: true
                , controlIconsEnabled: true
                , fit: 1
                , center: 1
                , customEventsHandler: eventsHandler
              })
            };
            await drawDiagram();
          </script>
        </body>    
    </p>

    </body>
    </html>
    
# Provenance

* Results from processing file Derive-Dr-Gov-Defs.md on 2025-07-17 20:50
