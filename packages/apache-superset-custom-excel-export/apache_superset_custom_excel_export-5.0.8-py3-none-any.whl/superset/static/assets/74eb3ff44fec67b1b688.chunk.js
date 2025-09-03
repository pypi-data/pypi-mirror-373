"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4229],{5007:(e,t,a)=>{function n(e){const t="CssEditor-css",a=document.head||document.getElementsByTagName("head")[0],n=document.querySelector(`.${t}`)||function(e){const t=document.createElement("style");return t.className=e,t.type="text/css",t}(t);return"styleSheet"in n?n.styleSheet.cssText=e:n.innerHTML=e,a.appendChild(n),function(){n.remove()}}a.d(t,{A:()=>n})},39093:(e,t,a)=>{a.d(t,{Au:()=>r,I8:()=>l,J:()=>d,l6:()=>o});var n=a(35742),s=a(5362);const i=(e,t,a)=>{let n=`/api/v1/dashboard/${e}/filter_state`;return t&&(n=n.concat(`/${t}`)),a&&(n=n.concat(`?tab_id=${a}`)),n},o=(e,t,a,o)=>n.A.put({endpoint:i(e,a,o),jsonPayload:{value:t}}).then((e=>e.json.message)).catch((e=>(s.A.error(e),null))),r=(e,t,a)=>n.A.post({endpoint:i(e,void 0,a),jsonPayload:{value:t}}).then((e=>e.json.key)).catch((e=>(s.A.error(e),null))),l=(e,t)=>n.A.get({endpoint:i(e,t)}).then((({json:e})=>JSON.parse(e.value))).catch((e=>(s.A.error(e),null))),d=e=>n.A.get({endpoint:`/api/v1/dashboard/permalink/${e}`}).then((({json:e})=>e)).catch((e=>(s.A.error(e),null)))},47986:(e,t,a)=>{a.d(t,{z:()=>i});var n=a(73992);function s(e,t){return e.length===Object.keys(t).length}function i(e,t,a){var i;let o=[];const r=Object.keys(a).includes(e)&&(0,n.Ub)(t),l=Array.isArray(t.scope)?t.scope:null!=(i=t.chartsInScope)?i:[];r&&(o=function(e,t,a){if(!t[e])return[];const n=[...a.filter((t=>String(t)!==e)),Number(e)],i=new Set(a);return Object.values(t).reduce(((a,o)=>o.slice_id===Number(e)?a:s(n,t)?(a.push(o.slice_id),a):(i.has(o.slice_id)&&a.push(o.slice_id),a)),[])}(e,a,l));const d=t;return(!r||(0,n.ve)(d)||(0,n.qQ)(d))&&(o=function(e,t){if(s(t,e))return Object.keys(e).map(Number);const a=new Set(t);return Object.values(e).reduce(((e,t)=>(a.has(t.slice_id)&&e.push(t.slice_id),e)),[])}(a,l)),o}},92008:(e,t,a)=>{a.d(t,{R:()=>s,W:()=>n});const n=(e,t)=>e[t]?{[t]:e[t]}:{},s=({chartConfiguration:e,nativeFilters:t,dataMask:a,allSliceIds:n})=>{const s={},i=Object.values(a).some((({id:e})=>{var a;const n=null==t||null==(a=t[e])||null==(a=a.scope)?void 0:a.selectedLayers;return n&&n.length>0}));let o=[],r=[];return i&&Object.values(a).forEach((({id:e})=>{var a,n;const s=null==t||null==(a=t[e])||null==(a=a.scope)?void 0:a.selectedLayers,i=(null==t||null==(n=t[e])||null==(n=n.scope)?void 0:n.excluded)||[];s&&s.length>0&&(o=s,r=i)})),Object.values(a).forEach((({id:a,extraFormData:l={}})=>{var d,c,u,h,p,f,b,v,g;let m=null!=(d=null!=(c=null!=(u=null==t||null==(h=t[a])?void 0:h.chartsInScope)?u:null==e||null==(p=e[parseInt(a,10)])||null==(p=p.crossFilters)?void 0:p.chartsInScope)?c:n)?d:[];const y=null==t||null==(f=t[a])?void 0:f.filterType,w=null==t||null==(b=t[a])?void 0:b.targets;let S,x=null==t||null==(v=t[a])||null==(v=v.scope)?void 0:v.selectedLayers,E=(null==t||null==(g=t[a])||null==(g=g.scope)?void 0:g.excluded)||[];if(!i||x&&0!==x.length||(x=o,E=r),x&&x.length>0){const e=(e=>{const t={},a=new Set;return e.forEach((e=>{const n=e.match(/^chart-(\d+)-layer-(\d+)$/);if(n){const e=parseInt(n[1],10),s=parseInt(n[2],10);Number.isNaN(e)||(t[e]||(t[e]=[]),t[e].push(s),a.add(e))}})),{layerMap:t,chartIds:a}})(x);S=e.layerMap;const t=new Set(e.chartIds);m.forEach((e=>{E.includes(e)||x.some((t=>t.startsWith(`chart-${e}-layer-`)))||t.add(e)})),m=Array.from(t)}else m=m.filter((e=>!E.includes(e)));s[a]={scope:m,targets:w||[],values:l,filterType:y,...S&&{layerScope:S}}})),s}},94229:(e,t,a)=>{a.r(t),a.d(t,{DashboardPage:()=>ce,DashboardPageIdContext:()=>oe,default:()=>ue});var n=a(2445),s=a(96540),i=a(17437),o=a(61574),r=a(72234),l=a(95579),d=a(61225),c=a(1081),u=a(5261),h=a(52879),p=a(71478),f=a(52123),b=a(34975),v=a(5007),g=a(92008),m=a(68921),y=a(62221),w=a(27023),S=a(32132),x=a(72173),E=a(39093),C=a(82960),I=a(5556),D=a.n(I),_=a(44344),$=a(38708),F=a(49588);function O(e){return Object.values(e).reduce(((e,t)=>(t&&t.type===F.oT&&t.meta&&t.meta.chartId&&e.push(t.meta.chartId),e)),[])}var k=a(4881),M=a(35700),j=a(35839),T=a(37725);const U=[F.oT,F.xY,F.rG];function z(e){return!Object.values(e).some((({type:e})=>e&&U.includes(e)))}var R=a(47986);const A={actions:D().shape({addSliceToDashboard:D().func.isRequired,removeSliceFromDashboard:D().func.isRequired,triggerQuery:D().func.isRequired,logEvent:D().func.isRequired,clearDataMaskState:D().func.isRequired}).isRequired,dashboardId:D().number.isRequired,editMode:D().bool,isPublished:D().bool,hasUnsavedChanges:D().bool,slices:D().objectOf(k.VE).isRequired,activeFilters:D().object.isRequired,chartConfiguration:D().object,datasources:D().object.isRequired,ownDataCharts:D().object.isRequired,layout:D().object.isRequired,impressionId:D().string.isRequired,timeout:D().number,userId:D().string,children:D().node};class P extends s.PureComponent{static onBeforeUnload(e){e?window.addEventListener("beforeunload",P.unload):window.removeEventListener("beforeunload",P.unload)}static unload(){const e=(0,l.t)("You have unsaved changes.");return window.event.returnValue=e,e}constructor(e){var t,a;super(e),this.appliedFilters=null!=(t=e.activeFilters)?t:{},this.appliedOwnDataCharts=null!=(a=e.ownDataCharts)?a:{},this.onVisibilityChange=this.onVisibilityChange.bind(this)}componentDidMount(){const e=(0,$.Ay)(),{editMode:t,isPublished:a,layout:n}=this.props,s={is_soft_navigation:M.Vy.timeOriginOffset>0,is_edit_mode:t,mount_duration:M.Vy.getTimestamp(),is_empty:z(n),is_published:a,bootstrap_data_length:e.length},i=(0,T.A)();i&&(s.target_id=i),this.props.actions.logEvent(M.es,s),"hidden"===document.visibilityState&&(this.visibilityEventData={start_offset:M.Vy.getTimestamp(),ts:(new Date).getTime()}),window.addEventListener("visibilitychange",this.onVisibilityChange),this.applyCharts()}componentDidUpdate(){this.applyCharts()}UNSAFE_componentWillReceiveProps(e){const t=O(this.props.layout),a=O(e.layout);this.props.dashboardId===e.dashboardId&&(t.length<a.length?a.filter((e=>-1===t.indexOf(e))).forEach((t=>{return this.props.actions.addSliceToDashboard(t,(a=e.layout,n=t,Object.values(a).find((e=>e&&e.type===F.oT&&e.meta&&e.meta.chartId===n))));var a,n})):t.length>a.length&&t.filter((e=>-1===a.indexOf(e))).forEach((e=>this.props.actions.removeSliceFromDashboard(e))))}applyCharts(){const{activeFilters:e,ownDataCharts:t,chartConfiguration:a,hasUnsavedChanges:n,editMode:s}=this.props,{appliedFilters:i,appliedOwnDataCharts:o}=this;a&&(s||(0,j.r$)(o,t,{ignoreUndefined:!0})&&(0,j.r$)(i,e,{ignoreUndefined:!0})||this.applyFilters(),n?P.onBeforeUnload(!0):P.onBeforeUnload(!1))}componentWillUnmount(){window.removeEventListener("visibilitychange",this.onVisibilityChange),this.props.actions.clearDataMaskState()}onVisibilityChange(){if("hidden"===document.visibilityState)this.visibilityEventData={start_offset:M.Vy.getTimestamp(),ts:(new Date).getTime()};else if("visible"===document.visibilityState){const e=this.visibilityEventData.start_offset;this.props.actions.logEvent(M.Xj,{...this.visibilityEventData,duration:M.Vy.getTimestamp()-e})}}applyFilters(){const{appliedFilters:e}=this,{activeFilters:t,ownDataCharts:a,slices:n}=this.props,s=Object.keys(t),i=Object.keys(e),o=new Set(s.concat(i)),r=((e,t)=>{const a=Object.keys(e),n=Object.keys(t),s=(i=a,o=n,[...i.filter((e=>!o.includes(e))),...o.filter((e=>!i.includes(e)))]).filter((a=>e[a]||t[a]));var i,o;return new Set([...a,...n]).forEach((a=>{(0,j.r$)(e[a],t[a])||s.push(a)})),[...new Set(s)]})(a,this.appliedOwnDataCharts);[...o].forEach((a=>{if(!s.includes(a)&&i.includes(a))r.push(...(0,R.z)(a,e[a],n));else if(i.includes(a)){if((0,j.r$)(e[a].values,t[a].values,{ignoreUndefined:!0})||r.push(...(0,R.z)(a,t[a],n)),!(0,j.r$)(e[a].scope,t[a].scope)){const n=(t[a].scope||[]).concat(e[a].scope||[]);r.push(...n)}}else r.push(...(0,R.z)(a,t[a],n))})),this.refreshCharts([...new Set(r)]),this.appliedFilters=t,this.appliedOwnDataCharts=a}refreshCharts(e){e.forEach((e=>{this.props.actions.triggerQuery(!0,e)}))}render(){return this.context.loading?(0,n.Y)(h.R,{}):this.props.children}}P.contextType=_.bf,P.propTypes=A,P.defaultProps={timeout:60,userId:""};const q=P;var L=a(2514),V=a(7735),H=a(95004);const N=(0,d.Ng)((function(e){var t,a;const{datasources:n,sliceEntities:s,dashboardInfo:i,dashboardState:o,dashboardLayout:r,impressionId:l}=e;return{timeout:null==(t=i.common)||null==(t=t.conf)?void 0:t.SUPERSET_WEBSERVER_TIMEOUT,userId:i.userId,dashboardId:i.id,editMode:o.editMode,isPublished:o.isPublished,hasUnsavedChanges:o.hasUnsavedChanges,datasources:n,chartConfiguration:null==(a=i.metadata)?void 0:a.chart_configuration,slices:s.slices,layout:r.present,impressionId:l}}),(function(e){return{actions:(0,C.zH)({setDatasources:b.nC,clearDataMaskState:H.V9,addSliceToDashboard:x.ft,removeSliceFromDashboard:x.Hg,triggerQuery:L.triggerQuery,logEvent:V.logEvent},e)}}))(q);var W=a(43561);const Y=e=>i.AH`
  body {
    h1 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeXXL}px;
      letter-spacing: -0.2px;
      margin-top: ${3*e.sizeUnit}px;
      margin-bottom: ${3*e.sizeUnit}px;
    }

    h2 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeXL}px;
      margin-top: ${3*e.sizeUnit}px;
      margin-bottom: ${2*e.sizeUnit}px;
    }

    h3,
    h4,
    h5,
    h6 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeLG}px;
      letter-spacing: 0.2px;
      margin-top: ${2*e.sizeUnit}px;
      margin-bottom: ${e.sizeUnit}px;
    }
  }
`,B=e=>i.AH`
  .header-title a {
    margin: ${e.sizeUnit/2}px;
    padding: ${e.sizeUnit/2}px;
  }
  .header-controls {
    &,
    &:hover {
      margin-top: ${e.sizeUnit}px;
    }
  }
`,X=e=>i.AH`
  .ant-dropdown-menu.chart-context-menu {
    min-width: ${43*e.sizeUnit}px;
  }
  .ant-dropdown-menu-submenu.chart-context-submenu {
    max-width: ${60*e.sizeUnit}px;
    min-width: ${40*e.sizeUnit}px;
  }
`,Q=e=>i.AH`
  a,
  .ant-tabs-tabpane,
  .ant-tabs-tab-btn,
  .superset-button,
  .superset-button.ant-dropdown-trigger,
  .header-controls span {
    &:focus-visible {
      box-shadow: 0 0 0 2px ${e.colorPrimaryText};
      border-radius: ${e.borderRadius}px;
      outline: none;
      text-decoration: none;
    }
    &:not(
      .superset-button,
      .ant-menu-item,
      a,
      .fave-unfave-icon,
      .ant-tabs-tabpane,
      .header-controls span
    ) {
      &:focus-visible {
        padding: ${e.sizeUnit/2}px;
      }
    }
  }
`;var K=a(71086),G=a.n(K),J=a(44383),Z=a.n(J),ee=a(55556);const te={},ae=()=>{const e=(0,y.Gq)(y.Hh.DashboardExploreContext,{});return G()(e,(e=>!e.isRedundant))},ne=(e,t)=>{const a=ae();(0,y.SO)(y.Hh.DashboardExploreContext,{...a,[e]:{...t,dashboardPageId:e}})},se=(0,c.Mz)([e=>e.dashboardInfo.metadata,e=>e.dashboardInfo.id,e=>{var t;return null==(t=e.dashboardState)?void 0:t.colorScheme},e=>{var t;return null==(t=e.nativeFilters)?void 0:t.filters},e=>e.dataMask,e=>{var t;return(null==(t=e.dashboardState)?void 0:t.sliceIds)||[]}],((e,t,a,n,s,i)=>{const o=Object.keys(n).reduce(((e,t)=>(e[t]=Z()(n[t],["chartsInScope"]),e)),{}),r=(0,g.R)({chartConfiguration:(null==e?void 0:e.chart_configuration)||te,nativeFilters:n,dataMask:s,allSliceIds:i});return{labelsColor:(null==e?void 0:e.label_colors)||te,labelsColorMap:(null==e?void 0:e.map_label_colors)||te,sharedLabelsColors:(0,ee.ik)(null==e?void 0:e.shared_label_colors),colorScheme:a,chartConfiguration:(null==e?void 0:e.chart_configuration)||te,nativeFilters:o,dataMask:s,dashboardId:t,filterBoxFilters:(0,m.ug)(),activeFilters:r}})),ie=({dashboardPageId:e})=>{const t=(0,d.d4)(se);return(0,s.useEffect)((()=>(ne(e,t),()=>{ne(e,{...t,isRedundant:!0})})),[t,e]),null},oe=(0,s.createContext)(""),re=(0,s.lazy)((()=>Promise.all([a.e(9467),a.e(2120),a.e(7379),a.e(2219),a.e(2656),a.e(817),a.e(240),a.e(7688),a.e(9074),a.e(8543),a.e(8604),a.e(7252),a.e(8873),a.e(960),a.e(5026)]).then(a.bind(a,29617)))),le=(0,c.Mz)((e=>e.dataMask),(e=>(0,g.W)(e,"ownState"))),de=(0,c.Mz)([e=>{var t;return null==(t=e.dashboardInfo.metadata)?void 0:t.chart_configuration},e=>e.nativeFilters.filters,e=>e.dataMask,e=>e.dashboardState.sliceIds],((e,t,a,n)=>({...(0,m.ug)(),...(0,g.R)({chartConfiguration:e,nativeFilters:t,dataMask:a,allSliceIds:n})}))),ce=({idOrSlug:e})=>{const t=(0,r.DP)(),a=(0,d.wA)(),c=(0,o.W6)(),g=(0,s.useMemo)((()=>(0,W.Ak)()),[]),m=(0,d.d4)((({dashboardInfo:e})=>e&&Object.keys(e).length>0)),{addDangerToast:C}=(0,u.Yf)(),{result:I,error:D}=(0,p.MZ)(e),{result:_,error:$}=(0,p.DT)(e),{result:F,error:O,status:k}=(0,p.RO)(e),M=(0,s.useRef)(!1),j=D||$,T=Boolean(I&&_),{dashboard_title:U,css:z,id:R=0}=I||{};(0,s.useEffect)((()=>{const e=()=>{const e=ae();(0,y.SO)(y.Hh.DashboardExploreContext,{...e,[g]:{...e[g],isRedundant:!0}})};return window.addEventListener("beforeunload",e),()=>{window.removeEventListener("beforeunload",e)}}),[g]),(0,s.useEffect)((()=>{a((0,x.wh)(k))}),[a,k]),(0,s.useEffect)((()=>{R&&async function(){const e=(0,S.P3)(w.vX.permalinkKey),t=(0,S.P3)(w.vX.nativeFiltersKey),n=(0,S.P3)(w.vX.nativeFilters);let s,i=t||{};if(e){const t=await(0,E.J)(e);t&&({dataMask:i,activeTabs:s}=t.state)}else t&&(i=await(0,E.I8)(R,t));n&&(i=n),T&&(M.current||(M.current=!0),a((0,f.M)({history:c,dashboard:I,charts:_,activeTabs:s,dataMask:i})))}()}),[T]),(0,s.useEffect)((()=>(U&&(document.title=U),()=>{document.title="Superset"})),[U]),(0,s.useEffect)((()=>"string"==typeof z?(0,v.A)(z):()=>{}),[z]),(0,s.useEffect)((()=>{O?C((0,l.t)("Error loading chart datasources. Filters may not work correctly.")):a((0,b.nC)(F))}),[C,F,O,a]);const A=(0,d.d4)(le),P=(0,d.d4)(de);if(j)throw j;const q=(0,s.useMemo)((()=>[i.AH`
  .filter-card-tooltip {
    &.ant-tooltip-placement-bottom {
      padding-top: 0;
      & .ant-tooltip-arrow {
        top: -13px;
      }
    }
  }
`,Y(t),X(t),Q(t),B(t)]),[t]);if(j)throw j;const L=(0,s.useMemo)((()=>(0,n.Y)(re,{})),[]);return(0,n.FD)(n.FK,{children:[(0,n.Y)(i.mL,{styles:q}),T&&m?(0,n.FD)(n.FK,{children:[(0,n.Y)(ie,{dashboardPageId:g}),(0,n.Y)(oe.Provider,{value:g,children:(0,n.Y)(N,{activeFilters:P,ownDataCharts:A,children:L})})]}):(0,n.Y)(h.R,{})]})},ue=ce}}]);