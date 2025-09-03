(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4943],{4943:(e,t,a)=>{"use strict";a.r(t),a.d(t,{default:()=>ie});var i=a(7240),n=a(72234),s=a(5556),o=a.n(s),r=a(7350),l=a.n(r),c=a(20249),h=a.n(c),m=a(24143),u=a.n(m),d=a(74353),p=a.n(d),y=a(83826),x=a.n(y),g=a(71111),b=a.n(g),f=a(7349),v=a(58928),A=a(94963),w=a(93641),k=a(32142),L=a(95579),T=a(53682),M=a(13270),$=a(36673);function C(e){return Object.keys(e).reduce(((e,t)=>{const a=e;return a[t]=t,a}),{})}const E=C({FORMULA:{value:"FORMULA",label:(0,L.t)("Formula")},EVENT:{value:"EVENT",label:(0,L.t)("Event"),supportNativeSource:!0},INTERVAL:{value:"INTERVAL",label:(0,L.t)("Interval"),supportNativeSource:!0},TIME_SERIES:{value:"TIME_SERIES",label:(0,L.t)("Time Series")}}),N=(E.FORMULA,C({NATIVE:{value:"NATIVE",label:"Superset annotation"}})),S={descriptionColumns:["long_descr"],intervalEndColumn:"end_dttm",timeColumn:"start_dttm",titleColumn:"short_descr"};function O(e){return e.sourceType===N.NATIVE?{...e,...S}:e}const F=E;var D=a(84338),I=a(17171);const B=o().oneOfType([o().number,o().oneOf(["auto"])]),z=o().oneOfType([o().string,o().shape({label:o().string})]),R=o().shape({r:o().number.isRequired,g:o().number.isRequired,b:o().number.isRequired}),Y=o().shape({x:o().number,y:o().number}),_=o().shape({x:o().string,y:o().number}),P=o().shape({outliers:o().arrayOf(o().number),Q1:o().number,Q2:o().number,Q3:o().number,whisker_high:o().number,whisker_low:o().number}),V=o().shape({markerLabels:o().arrayOf(o().string),markerLineLabels:o().arrayOf(o().string),markerLines:o().arrayOf(o().number),markers:o().arrayOf(o().number),measures:o().arrayOf(o().number),rangeLabels:o().arrayOf(o().string),ranges:o().arrayOf(o().number)}),W=o().shape({annotationType:o().oneOf(Object.keys(E)),color:o().string,hideLine:o().bool,name:o().string,opacity:o().string,show:o().bool,showMarkers:o().bool,sourceType:o().string,style:o().string,value:o().oneOfType([o().number,o().string]),width:o().number}),U=[{text:"No data",dy:"-.75em",class:"header"},{text:"Adjust filters or check the Datasource.",dy:".75em",class:"body"}];p().extend(x());const G=(0,f.mo)(v.M);b().utils.noData=function(e,t){const a=e.options().margin(),i=b().utils.availableHeight(null,t,a),n=b().utils.availableWidth(null,t,a),s=a.left+n/2,o=a.top+i/2;t.selectAll("g").remove();const r=t.selectAll(".nv-noData").data(U);r.enter().append("text").attr("class",(e=>`nvd3 nv-noData ${e.class}`)).attr("dy",(e=>e.dy)).style("text-anchor","middle"),r.attr("x",s).attr("y",o).text((e=>e.text))};const{getColor:j,getScale:q}=A,H=[w.Y.Compare,w.Y.TimePivot],Q={data:o().oneOfType([o().arrayOf(o().oneOfType([_,o().shape({key:o().string,values:o().arrayOf(_)}),o().shape({key:o().arrayOf(o().string),values:o().arrayOf(Y)}),o().shape({classed:o().string,key:o().string,type:o().string,values:o().arrayOf(Y),yAxis:o().number}),o().shape({label:o().string,values:o().arrayOf(P)}),o().shape({key:o().string,values:o().arrayOf(o().object)})])),V]),width:o().number,height:o().number,annotationData:o().object,annotationLayers:o().arrayOf(W),bottomMargin:B,colorScheme:o().string,comparisonType:o().string,contribution:o().bool,leftMargin:B,onError:o().func,showLegend:o().bool,showMarkers:o().bool,vizType:o().oneOf([w.Y.BoxPlot,"bubble",w.Y.Bullet,w.Y.Compare,"column",w.Y.TimePivot,"pie"]),xAxisFormat:o().string,numberFormat:o().string,xAxisLabel:o().string,xAxisShowMinMax:o().bool,xIsLogScale:o().bool,xTicksLayout:o().oneOf(["auto","staggered","45°"]),yAxisFormat:o().string,yAxisBounds:o().arrayOf(o().number),yAxisLabel:o().string,yAxisShowMinMax:o().bool,yIsLogScale:o().bool,isBarStacked:o().bool,showBarValue:o().bool,showBrush:o().oneOf([!0,"yes",!1,"no","auto"]),onBrushEnd:o().func,yAxis2Format:o().string,lineInterpolation:o().string,isDonut:o().bool,isPieLabelOutside:o().bool,pieLabelType:o().oneOf(["key","value","percent","key_value","key_percent","key_value_percent"]),showLabels:o().bool,entity:o().string,maxBubbleSize:o().number,xField:z,yField:z,sizeField:z,baseColor:R},X=()=>{},J=(0,k.gV)();function K(e,t){const{data:a,width:i,height:n,annotationData:s,annotationLayers:o=[],baseColor:r,bottomMargin:c,colorScheme:m,comparisonType:d,contribution:y,entity:x,isBarStacked:g,isDonut:v,isPieLabelOutside:A,leftMargin:C,lineInterpolation:E="linear",markerLabels:N,markerLines:S,markerLineLabels:B,markers:z,maxBubbleSize:R,onBrushEnd:Y=X,onError:_=X,pieLabelType:P,rangeLabels:V,ranges:W,showBarValue:U,showBrush:Q,showLabels:K,showLegend:Z,showMarkers:ee,sizeField:te,vizType:ae,xAxisFormat:ie,numberFormat:ne,xAxisLabel:se,xAxisShowMinMax:oe=!1,xField:re,xIsLogScale:le,xTicksLayout:ce,yAxisFormat:he,yAxisBounds:me,yAxisLabel:ue,yAxisShowMinMax:de=!1,yAxis2ShowMinMax:pe=!1,yField:ye,yIsLogScale:xe,sliceId:ge}=t,be=null!==document.querySelector("#explorer-container"),fe=e;fe.innerHTML="";const ve=o.filter((e=>e.show));let Ae,we=fe,ke=null;for(;we.parentElement;){if(we.parentElement.id.startsWith("chart-id-")){ke=we.parentElement.id;break}we=we.parentElement}const Le=i;let Te="key";function Me(e){return e.includes(ae)}fe.style.width=`${i}px`,fe.style.height=`${n}px`,ke?(0,I.G0)(ke):(0,I.$v)(!0),b().addGraph((function(){const t=u().select(e);t.classed("superset-legacy-chart-nvd3",!0),t.classed(`superset-legacy-chart-nvd3-${h()(ae)}`,!0);let o=t.select("svg");o.empty()&&(o=t.append("svg"));const fe=ae===w.Y.Bullet?Math.min(n,50):n,we=Me(H),$e="staggered"===ce,Ce="45°"===ce?45:0;if(45===Ce&&(0,D.A)(Q))return _((0,L.t)("You cannot use 45° tick layout along with the time range filter")),null;const Ee=(0,D.A)(Q)||"auto"===Q&&n>=480&&"45°"!==ce,Ne=(0,k.gV)(ne);switch(ae){case w.Y.TimePivot:Ae=b().models.lineChart(),Ae.xScale(u().time.scale.utc()),Ae.interpolate(E);break;case w.Y.Pie:if(Ae=b().models.pieChart(),Te="x",Ae.valueFormat(Ne),v&&Ae.donut(!0),Ae.showLabels(K),Ae.labelsOutside(A),Ae.labelThreshold(.05),Ae.cornerRadius(!0),["key","value","percent"].includes(P))Ae.labelType(P);else if("key_value"===P)Ae.labelType((e=>`${e.data.x}: ${Ne(e.data.y)}`));else{const e=u().sum(a,(e=>e.y)),t=(0,k.gV)(T.A.PERCENT_2_POINT);"key_percent"===P?(Ae.tooltip.valueFormatter((e=>t(e))),Ae.labelType((a=>`${a.data.x}: ${t(a.data.y/e)}`))):(Ae.tooltip.valueFormatter((a=>`${Ne(a)} (${t(a/e)})`)),Ae.labelType((a=>`${a.data.x}: ${Ne(a.data.y)} (${t(a.data.y/e)})`)))}Ae.margin({top:0});break;case"column":Ae=b().models.multiBarChart().reduceXTicks(!1);break;case w.Y.Compare:Ae=b().models.cumulativeLineChart(),Ae.xScale(u().time.scale.utc()),Ae.useInteractiveGuideline(!0),Ae.xAxis.showMaxMin(!1);break;case w.Y.LegacyBubble:Ae=b().models.scatterChart(),Ae.showDistX(!1),Ae.showDistY(!1),Ae.tooltip.contentGenerator((e=>(0,I.oh)({point:e.point,entity:x,xField:re,yField:ye,sizeField:te,xFormatter:(0,I.wn)(ie),yFormatter:(0,I.wn)(he),sizeFormatter:J}))),Ae.pointRange([5,R**2]),Ae.pointDomain([0,u().max(a,(e=>u().max(e.values,(e=>e.size))))]);break;case w.Y.BoxPlot:Te="label",Ae=b().models.boxPlotChart(),Ae.x((e=>e.label)),Ae.maxBoxWidth(75);break;case w.Y.Bullet:Ae=b().models.bulletChart(),a.rangeLabels=V,a.ranges=W,a.markerLabels=N,a.markerLines=S,a.markerLineLabels=B,a.markers=z;break;default:throw new Error(`Unrecognized visualization for nvd3${ae}`)}let Se;Ae.margin({left:0,bottom:0}),U&&((0,I.C$)(o,a,g,he),Ae.dispatch.on("stateChange.drawBarValues",(()=>{(0,I.C$)(o,a,g,he)}))),Ee&&Y!==X&&Ae.focus&&Ae.focus.dispatch.on("brush",(e=>{const t=(0,I.EF)(e.extent);t&&e.brush.on("brushend",(()=>{Y(t)}))})),Ae.xAxis&&Ae.xAxis.staggerLabels&&Ae.xAxis.staggerLabels($e),Ae.xAxis&&Ae.xAxis.rotateLabels&&Ae.xAxis.rotateLabels(Ce),Ae.x2Axis&&Ae.x2Axis.staggerLabels&&Ae.x2Axis.staggerLabels($e),Ae.x2Axis&&Ae.x2Axis.rotateLabels&&Ae.x2Axis.rotateLabels(Ce),"showLegend"in Ae&&void 0!==Z&&(Le<340&&ae!==w.Y.Pie?Ae.showLegend(!1):Ae.showLegend(Z)),xe&&Ae.yScale(u().scale.log()),le&&Ae.xScale(u().scale.log()),we?(Se=(0,f.mo)(ie),Ae.interactiveLayer.tooltip.headerFormatter(G)):Se=(0,I.wn)(ie),Ae.x2Axis&&Ae.x2Axis.tickFormat&&Ae.x2Axis.tickFormat(Se),Ae.xAxis&&Ae.xAxis.tickFormat&&(Me([w.Y.BoxPlot])?Ae.xAxis.tickFormat((e=>e.length>40?`${e.slice(0,Math.max(0,40))}…`:e)):Ae.xAxis.tickFormat(Se));let Oe=(0,I.wn)(he);if(Ae.yAxis&&Ae.yAxis.tickFormat&&(!y&&"percentage"!==d||he&&he!==T.A.SMART_NUMBER&&he!==T.A.SMART_NUMBER_SIGNED||(Oe=(0,k.gV)(T.A.PERCENT_1_POINT)),Ae.yAxis.tickFormat(Oe)),Ae.y2Axis&&Ae.y2Axis.tickFormat&&Ae.y2Axis.tickFormat(Oe),Ae.yAxis&&Ae.yAxis.ticks(5),Ae.y2Axis&&Ae.y2Axis.ticks(5),(0,I.dw)(Ae.xAxis,oe),(0,I.dw)(Ae.x2Axis,oe),(0,I.dw)(Ae.yAxis,de),(0,I.dw)(Ae.y2Axis,pe||de),ae===w.Y.TimePivot){if(r){const{r:e,g:t,b:a}=r;Ae.color((i=>{const n=i.rank>0?.5*i.perc:1;return`rgba(${e}, ${t}, ${a}, ${n})`}))}Ae.useInteractiveGuideline(!0),Ae.interactiveLayer.tooltip.contentGenerator((e=>(0,I.qY)(e,Se,Oe)))}else if(ae!==w.Y.Bullet){const e=q(m);Ae.color((t=>t.color||e((0,I.n0)(t[Te]),ge)))}Me([w.Y.Compare])&&Ae.interactiveLayer.tooltip.contentGenerator((e=>(0,I.Jy)(e,Oe))),Ae.width(Le),Ae.height(fe),o.datum(a).transition().duration(500).attr("height",fe).attr("width",Le).call(Ae),xe&&Ae.yAxis.tickFormat((e=>0!==e&&Math.log10(e)%1==0?Oe(e):"")),Ce>0&&o.select(".nv-x.nv-axis > g").selectAll("g").selectAll("text").attr("dx",-6.5);const Fe=()=>{if(Ae.yDomain&&Array.isArray(me)&&2===me.length){const[e,t]=me,i=(0,M.A)(e)&&!Number.isNaN(e),n=(0,M.A)(t)&&!Number.isNaN(t);if(i&&n)Ae.yDomain([e,t]),Ae.clipEdge(!0);else if(i||n){const[s,o]=(0,I.B2)(a),r=i?e:s,l=n?t:o;Ae.yDomain([r,l]),Ae.clipEdge(!0)}}};if(Fe(),Ae.dispatch&&Ae.dispatch.stateChange&&Ae.dispatch.on("stateChange.applyYAxisBounds",Fe),ee&&(o.selectAll(".nv-point").style("stroke-opacity",1).style("fill-opacity",1),Ae.dispatch.on("stateChange.showMarkers",(()=>{setTimeout((()=>{o.selectAll(".nv-point").style("stroke-opacity",1).style("fill-opacity",1)}),10)}))),void 0!==Ae.yAxis||void 0!==Ae.yAxis2){const t=Math.ceil(Math.min(i*(be?.01:.03),30)),n=Ae.margin();Ae.xAxis&&(n.bottom=28);const r=(0,I.cm)(o,Ae.yAxis2?"nv-y1":"nv-y"),h=(0,I.cm)(o,"nv-x");if(n.left=r+t,ue&&""!==ue&&(n.left+=25),U&&(n.top+=24),oe&&(n.right=Math.max(20,h/2)+t),45===Ce?(n.bottom=h*Math.sin(Math.PI*Ce/180)+t+30,n.right=h*Math.cos(Math.PI*Ce/180)+t):$e&&(n.bottom=40),c&&"auto"!==c&&(n.bottom=parseInt(c,10)),C&&"auto"!==C&&(n.left=C),se&&""!==se&&Ae.xAxis){n.bottom+=25;let e=0;n.bottom&&!Number.isNaN(n.bottom)&&(e=n.bottom-45),Ae.xAxis.axisLabel(se).axisLabelDistance(e)}if(ue&&""!==ue&&Ae.yAxis){let e=0;n.left&&!Number.isNaN(n.left)&&(e=n.left-70),Ae.yAxis.axisLabel(ue).axisLabelDistance(e)}if(we&&s&&ve.length>0){const e=ve.filter((e=>e.annotationType===F.TIME_SERIES)).reduce(((e,t)=>e.concat((s[t.name]||[]).map((e=>{if(!e)return{};const a=Array.isArray(e.key)?`${t.name}, ${e.key.join(", ")}`:`${t.name}, ${e.key}`;return{...e,key:a,color:t.color,strokeWidth:t.width,classed:`${t.opacity} ${t.style} nv-timeseries-annotation-layer showMarkers${t.showMarkers} hideLine${t.hideLine}`}})))),[]);a.push(...e)}if(ke&&(Ae&&Ae.interactiveLayer&&Ae.interactiveLayer.tooltip&&Ae.interactiveLayer.tooltip.classes([(0,I.Ir)(ke)]),Ae&&Ae.tooltip&&Ae.tooltip.classes([(0,I.Ir)(ke)])),Ae.margin(n),o.datum(a).transition().duration(500).attr("width",Le).attr("height",fe).call(Ae),window.addEventListener("scroll",l()((()=>(0,I.$v)(!1)),250)),we&&ve.length>0){const t=ve.filter((e=>e.annotationType===F.FORMULA)),i=Ae.xAxis.scale().domain()[1].valueOf(),n=Ae.xAxis.scale().domain()[0].valueOf();let r;if(r=Ae.xScale?Ae.xScale():Ae.xAxis.scale?Ae.xAxis.scale():u().scale.linear(),r&&r.clamp&&r.clamp(!0),t.length>0){const e=[];let s=Math.min(...a.map((e=>Math.min(...e.values.slice(1).map(((t,a)=>t.x-e.values[a].x))))));const o=(i-n)/(s||1);s=o<100?(i-n)/100:s,s=o>500?(i-n)/500:s,e.push(n);for(let t=n;t<i;t+=s)e.push(t);e.push(i);const r=t.map((t=>{const{value:a}=t;return{key:t.name,values:e.map((e=>({x:e,y:(0,$.p)(a,e)}))),color:t.color,strokeWidth:t.width,classed:`${t.opacity} ${t.style}`}}));a.push(...r)}const l=Ae.xAxis1?Ae.xAxis1:Ae.xAxis,c=Ae.yAxis1?Ae.yAxis1:Ae.yAxis,h=l.scale().range()[1],d=c.scale().range()[0];s&&(ve.filter((e=>e.annotationType===F.EVENT&&s&&s[e.name])).forEach(((t,a)=>{const i=O(t),n=u().select(e).select(".nv-wrap").append("g").attr("class",`nv-event-annotation-layer-${a}`),o=i.color||j((0,I.n0)(i.name),m),l=(0,I.AN)({...i,annotationTipClass:`arrow-down nv-event-annotation-layer-${t.sourceType}`}),c=(s[i.name].records||[]).map((e=>{const t=new Date(p().utc(e[i.timeColumn]));return{...e,[i.timeColumn]:t}})).filter((e=>!Number.isNaN(e[i.timeColumn].getMilliseconds())));c.length>0&&n.selectAll("line").data(c).enter().append("line").attr({x1:e=>r(new Date(e[i.timeColumn])),y1:0,x2:e=>r(new Date(e[i.timeColumn])),y2:d}).attr("class",`${i.opacity} ${i.style}`).style("stroke",o).style("stroke-width",i.width).on("mouseover",l.show).on("mouseout",l.hide).call(l),Ae.focus&&Ae.focus.dispatch.on("onBrush.event-annotation",(()=>{n.selectAll("line").data(c).attr({x1:e=>r(new Date(e[i.timeColumn])),y1:0,x2:e=>r(new Date(e[i.timeColumn])),y2:d,opacity:e=>{const t=r(new Date(e[i.timeColumn]));return t>0&&t<h?1:0}})}))})),ve.filter((e=>e.annotationType===F.INTERVAL&&s&&s[e.name])).forEach(((t,a)=>{const i=O(t),n=u().select(e).select(".nv-wrap").append("g").attr("class",`nv-interval-annotation-layer-${a}`),o=i.color||j((0,I.n0)(i.name),m),l=(0,I.AN)(i),c=(s[i.name].records||[]).map((e=>{const t=new Date(p().utc(e[i.timeColumn])),a=new Date(p().utc(e[i.intervalEndColumn]));return{...e,[i.timeColumn]:t,[i.intervalEndColumn]:a}})).filter((e=>!Number.isNaN(e[i.timeColumn].getMilliseconds())&&!Number.isNaN(e[i.intervalEndColumn].getMilliseconds())));c.length>0&&n.selectAll("rect").data(c).enter().append("rect").attr({x:e=>Math.min(r(new Date(e[i.timeColumn])),r(new Date(e[i.intervalEndColumn]))),y:0,width:e=>Math.max(Math.abs(r(new Date(e[i.intervalEndColumn]))-r(new Date(e[i.timeColumn]))),1),height:d}).attr("class",`${i.opacity} ${i.style}`).style("stroke-width",i.width).style("stroke",o).style("fill",o).style("fill-opacity",.2).on("mouseover",l.show).on("mouseout",l.hide).call(l),Ae.focus&&Ae.focus.dispatch.on("onBrush.interval-annotation",(()=>{n.selectAll("rect").data(c).attr({x:e=>r(new Date(e[i.timeColumn])),width:e=>{const t=r(new Date(e[i.timeColumn]));return r(new Date(e[i.intervalEndColumn]))-t}})}))}))),o.datum(a).attr("height",fe).attr("width",Le).call(Ae),Ae.dispatch.on("renderEnd.timeseries-annotation",(()=>{u().selectAll(".slice_container .nv-timeseries-annotation-layer.showMarkerstrue .nv-point").style("stroke-opacity",1).style("fill-opacity",1),u().selectAll(".slice_container .nv-timeseries-annotation-layer.hideLinetrue").style("stroke-width",0)}))}}return(0,I.OK)(Ae),Ae}))}K.displayName="NVD3",K.propTypes=Q;const Z=K;var ee=a(2445);const te=(0,i.A)(Z,{componentWillUnmount:function(){const{id:e}=this.props;null!=e?(0,I.G0)(e):(0,I.$v)(!0)}}),ae=({className:e,...t})=>(0,ee.Y)("div",{className:e,children:(0,ee.Y)(te,{...t})});ae.propTypes={className:o().string.isRequired};const ie=(0,n.I4)(ae)`
  .superset-legacy-chart-nvd3-dist-bar,
  .superset-legacy-chart-nvd3-bar {
    overflow-x: auto !important;
    svg {
      &.nvd3-svg {
        width: auto;
        font-size: ${({theme:e})=>e.fontSize};
      }
    }
  }
  .superset-legacy-chart-nvd3 {
    nv-x text {
      font-size: ${({theme:e})=>e.fontSize};
    }
    g.superset path {
      stroke-dasharray: 5, 5;
    }
    .nvtooltip {
      table td {
        font-size: @font-size-s !important;
      }
    }
    .nvtooltip tr.highlight td {
      font-weight: ${({theme:e})=>e.fontWeightStrong};
      font-size: ${({theme:e})=>e.fontSize}px !important;
    }
    text.nv-axislabel {
      font-size: ${({theme:e})=>e.fontSize} !important;
    }
    g.solid path,
    line.solid {
      stroke-dasharray: unset;
    }
    g.dashed path,
    line.dashed {
      stroke-dasharray: 5, 5;
    }
    g.longDashed path,
    line.dotted {
      stroke-dasharray: 1, 1;
    }

    g.opacityLow path,
    line.opacityLow {
      stroke-opacity: 0.2;
    }

    g.opacityMedium path,
    line.opacityMedium {
      stroke-opacity: 0.5;
    }
    g.opacityHigh path,
    line.opacityHigh {
      stroke-opacity: 0.8;
    }
    g.time-shift-0 path,
    line.time-shift-0 {
      stroke-dasharray: 5, 5;
    }
    g.time-shift-1 path,
    line.time-shift-1 {
      stroke-dasharray: 1, 5;
    }
    g.time-shift-2 path,
    line.time-shift-3 {
      stroke-dasharray: 5, 1;
    }
    g.time-shift-3 path,
    line.time-shift-3 {
      stroke-dasharray: 5, 1;
    }
    g.time-shift-4 path,
    line.time-shift-4 {
      stroke-dasharray: 5, 10;
    }
    g.time-shift-5 path,
    line.time-shift-5 {
      stroke-dasharray: 0.9;
    }
    g.time-shift-6 path,
    line.time-shift-6 {
      stroke-dasharray: 15, 10, 5;
    }
    g.time-shift-7 path,
    line.time-shift-7 {
      stroke-dasharray: 15, 10, 5, 10;
    }
    g.time-shift-8 path,
    line.time-shift-8 {
      stroke-dasharray: 15, 10, 5, 10, 15;
    }
    g.time-shift-9 path,
    line.time-shift-9 {
      stroke-dasharray: 5, 5, 1, 5;
    }
    .nv-noData.body {
      font-size: ${({theme:e})=>e.fontSize};
      font-weight: ${({theme:e})=>e.fontWeightNormal};
    }
  }
  .superset-legacy-chart-nvd3-tr-highlight {
    border-top: 1px solid;
    border-bottom: 1px solid;
    font-weight: ${({theme:e})=>e.fontWeightStrong};
  }
  .superset-legacy-chart-nvd3-tr-total {
    font-weight: ${({theme:e})=>e.fontWeightStrong};
  }
  .nvtooltip {
    .tooltip-header {
      white-space: nowrap;
      font-weight: ${({theme:e})=>e.fontWeightStrong};
    }
    tbody tr:not(.tooltip-header) td:nth-of-type(2) {
      word-break: break-word;
    }
  }
  .d3-tip.nv-event-annotation-layer-table,
  .d3-tip.nv-event-annotation-layer-NATIVE {
    width: 200px;
    border-radius: 2px;
    background-color: ${({theme:e})=>e.colors.grayscale.base};
    fill-opacity: 0.6;
    margin: ${({theme:e})=>2*e.sizeUnit}px;
    padding: ${({theme:e})=>2*e.sizeUnit}px;
    color: ${({theme:e})=>e.colors.grayscale.light5};
    &:after {
      content: '\\25BC';
      font-size: ${({theme:e})=>e.fontSize};
      color: ${({theme:e})=>e.colors.grayscale.base};
      position: absolute;
      bottom: -14px;
      left: 94px;
    }
  }
`},7240:(e,t,a)=>{"use strict";a.d(t,{A:()=>s});var i=a(2445),n=a(96540);function s(e,t){class a extends n.Component{constructor(e){super(e),this.container=void 0,this.setContainerRef=this.setContainerRef.bind(this)}componentDidMount(){this.execute()}componentDidUpdate(){this.execute()}componentWillUnmount(){this.container=void 0,null!=t&&t.componentWillUnmount&&t.componentWillUnmount.bind(this)()}setContainerRef(e){this.container=e}execute(){this.container&&e(this.container,this.props)}render(){const{id:e,className:t}=this.props;return(0,i.Y)("div",{ref:this.setContainerRef,id:e,className:t})}}const s=a;return e.displayName&&(s.displayName=e.displayName),e.propTypes&&(s.propTypes={...s.propTypes,...e.propTypes}),e.defaultProps&&(s.defaultProps=e.defaultProps),a}},7350:(e,t,a)=>{var i=a(38221),n=a(23805);e.exports=function(e,t,a){var s=!0,o=!0;if("function"!=typeof e)throw new TypeError("Expected a function");return n(a)&&(s="leading"in a?!!a.leading:s,o="trailing"in a?!!a.trailing:o),i(e,t,{leading:s,maxWait:t,trailing:o})}}}]);