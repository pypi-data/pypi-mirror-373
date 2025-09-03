"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[2416],{32416:(e,t,i)=>{i.d(t,{Ay:()=>W,rE:()=>$});var n,a=i(2445),l=i(96540),r=i(25929),o=i(46942),s=i.n(o),d=i(95579),c=i(72234),m=i(17437),p=i(58863),u=i(62683),h=i(17355),g=i(97470),x=i(82537),b=i(38380),v=i(40104),f=i(44344),z=i(13130);!function(e){e.AllCharts="ALL_CHARTS",e.Featured="FEATURED",e.Category="CATEGORY",e.Tags="TAGS"}(n||(n={}));const $=1090,y=(0,d.t)("Other"),C=(0,d.t)("All charts"),U=(0,d.t)("Featured"),Y=[U,(0,d.t)("ECharts"),(0,d.t)("Advanced-Analytics")],k="viz-type-control",w=c.I4.div`
  ${({isSelectedVizMetadata:e})=>`\n    display: grid;\n    grid-template-rows: ${e?"auto minmax(100px, 1fr) minmax(200px, 35%)":"auto minmax(100px, 1fr)"};\n    // em is used here because the sidebar should be sized to fit the longest standard tag\n    grid-template-columns: minmax(14em, auto) 5fr;\n    grid-template-areas:\n      'sidebar search'\n      'sidebar main'\n      'details details';\n    height: 70vh;\n    overflow: auto;\n  `}
`,S=c.I4.h3`
  margin-top: 0;
  margin-bottom: ${({theme:e})=>2*e.sizeUnit}px;
  font-size: ${({theme:e})=>e.fontSizeLG}px;
  font-weight: ${({theme:e})=>e.fontWeightStrong};
  line-height: ${({theme:e})=>6*e.sizeUnit}px;
`,A=c.I4.div`
  grid-area: sidebar;
  display: flex;
  flex-direction: column;
  border-right: 1px solid ${({theme:e})=>e.colorBorder};
  overflow: auto;

  .ant-collapse .ant-collapse-item {
    .ant-collapse-header {
      font-size: ${({theme:e})=>e.fontSizeSM}px;
      color: ${({theme:e})=>e.colorText};
      padding-left: ${({theme:e})=>2*e.sizeUnit}px;
      padding-bottom: ${({theme:e})=>e.sizeUnit}px;
    }

    .ant-collapse-content .ant-collapse-content-box {
      display: flex;
      flex-direction: column;
      padding: 0 ${({theme:e})=>2*e.sizeUnit}px;
    }
  }
`,F=c.I4.div`
  grid-area: main;
  overflow-y: auto;
`,I=c.I4.div`
  ${({theme:e})=>`\n    grid-area: search;\n    margin-top: ${3*e.sizeUnit}px;\n    margin-bottom: ${e.sizeUnit}px;\n    margin-left: ${3*e.sizeUnit}px;\n    margin-right: ${3*e.sizeUnit}px;\n    .ant-input-affix-wrapper {\n      padding-left: ${2*e.sizeUnit}px;\n    }\n  `}
`,M=c.I4.div`
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${({theme:e})=>e.colorIcon};
`,T=c.I4.button`
  ${({theme:e})=>`\n    all: unset; // remove default button styles\n    display: flex;\n    flex-direction: row;\n    align-items: center;\n    cursor: pointer;\n    margin: ${e.sizeUnit}px 0;\n    padding: 0 ${e.sizeUnit}px;\n    border-radius: ${e.borderRadius}px;\n    line-height: 2em;\n    text-overflow: ellipsis;\n    white-space: nowrap;\n    position: relative;\n    color: ${e.colorText};\n\n    &:focus {\n      outline: initial;\n    }\n\n    &.selected {\n      background-color: ${e.colorPrimaryBgHover};\n      color: ${e.colorPrimaryTextActive};\n\n      svg {\n        color: ${e.colorIcon};\n      }\n\n      &:hover {\n        .cancel {\n          visibility: visible;\n        }\n      }\n    }\n\n    & > span[role="img"] {\n      margin-right: ${2*e.sizeUnit}px;\n    }\n\n    .cancel {\n      visibility: hidden;\n    }\n  `}
`,E=c.I4.div`
  overflow: auto;
  display: grid;
  grid-template-columns: repeat(
    auto-fill,
    ${({theme:e})=>24*e.sizeUnit}px
  );
  grid-auto-rows: max-content;
  justify-content: space-evenly;
  grid-gap: ${({theme:e})=>2*e.sizeUnit}px;
  justify-items: center;
  // for some reason this padding doesn't seem to apply at the bottom of the container. Why is a mystery.
  padding: ${({theme:e})=>2*e.sizeUnit}px;
`,D=e=>m.AH`
  grid-area: details;
  border-top: 1px solid ${e.colorBorder};
`,O=e=>m.AH`
  padding: ${4*e.sizeUnit}px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto 1fr;
  grid-template-areas:
    'viz-name examples-header'
    'viz-tags examples'
    'description examples';
`,H=c.I4.div`
  grid-area: viz-tags;
  width: ${({theme:e})=>120*e.sizeUnit}px;
  padding-right: ${({theme:e})=>14*e.sizeUnit}px;
  padding-bottom: ${({theme:e})=>2*e.sizeUnit}px;
`,N=c.I4.p`
  grid-area: description;
  overflow: auto;
  padding-right: ${({theme:e})=>14*e.sizeUnit}px;
  margin: 0;
`,B=c.I4.div`
  grid-area: examples;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  overflow: auto;
  gap: ${({theme:e})=>4*e.sizeUnit}px;

  img {
    height: 100%;
    border-radius: ${({theme:e})=>e.borderRadius}px;
    border: 1px solid ${({theme:e})=>e.colorBorder};
  }
`,R=e=>m.AH`
  cursor: pointer;
  width: ${24*e.sizeUnit}px;
  position: relative;

  img {
    min-width: ${24*e.sizeUnit}px;
    min-height: ${24*e.sizeUnit}px;
    border: 1px solid ${e.colorBorder};
    border-radius: ${e.borderRadius}px;
    transition: border-color ${e.motionDurationMid};
  }

  &.selected img {
    border: 2px solid ${e.colorPrimaryBorder};
  }

  &:hover:not(.selected) img {
    border: 1px solid ${e.colorBorder};
  }

  .viztype-label {
    margin-top: ${2*e.sizeUnit}px;
    text-align: center;
  }
`,P=c.I4.div`
  ${({theme:e})=>`\n    border: 1px solid ${e.colorPrimaryText};\n    box-sizing: border-box;\n    border-radius: ${e.borderRadius}px;\n    background: ${e.colors.grayscale.light5};\n    line-height: ${2.5*e.sizeUnit}px;\n    color: ${e.colorPrimaryText};\n    font-size: ${e.fontSizeSM}px;\n    font-weight: ${e.fontWeightStrong};\n    text-align: center;\n    padding: ${.5*e.sizeUnit}px ${e.sizeUnit}px;\n    cursor: pointer;\n\n    div {\n      transform: scale(0.83,0.83);\n    }\n  `}
`,j=c.I4.div`
  position: absolute;
  right: ${({theme:e})=>e.sizeUnit}px;
  top: ${({theme:e})=>19*e.sizeUnit}px;
`,V=c.I4.div`
  display: inline-block !important;
  margin-left: ${({theme:e})=>2*e.sizeUnit}px;
`,_=({entry:e,selectedViz:t,setSelectedViz:i,onDoubleClick:n})=>{const l=(0,c.DP)(),{key:r,value:o}=e,s=t===e.key;return(0,a.FD)("div",{role:"button",css:R(l),tabIndex:0,className:s?"selected":"",onClick:()=>i(r),onDoubleClick:n,"data-test":"viztype-selector-container",children:[(0,a.Y)("img",{alt:o.name,width:"100%",className:"viztype-selector "+(s?"selected":""),src:o.thumbnail}),(0,a.Y)("div",{className:"viztype-label","data-test":`${k}__viztype-label`,children:o.name}),o.label&&(0,a.Y)(j,{children:(0,a.Y)(P,{children:(0,a.Y)("div",{children:(0,d.t)(o.label)})})})]})},G=({vizEntries:e,...t})=>(0,a.Y)(E,{"data-test":`${k}__viz-row`,children:e.map((e=>(0,a.Y)(_,{...t,entry:e},e.key)))}),L=({selector:e,sectionId:t,icon:i,isSelected:n,onClick:r,className:o})=>{const d=(0,l.useRef)(null);return(0,l.useEffect)((()=>{n&&queueMicrotask((()=>(0,z.A)(d.current,{behavior:"smooth",scrollMode:"if-needed"})))}),[]),(0,a.FD)(T,{"aria-label":e,"aria-selected":n,ref:d,name:e,className:s()(o,n&&"selected"),onClick:()=>r(e,t),tabIndex:0,role:"tab",children:[i,e]},e)},K=(e,t)=>t===e.category||t===y&&null==e.category||(e.tags||[]).indexOf(t)>-1;function W(e){var t,i;const{selectedViz:o,onChange:s,onDoubleClick:c,className:z,denyList:$}=e,{mountedPluginMetadata:T}=(0,f.Q)(),E=(0,l.useRef)(),[R,j]=(0,l.useState)(""),[_,W]=(0,l.useState)(!0),q=_&&!!R,J=o?T[o]:null,Q=(0,l.useMemo)((()=>Object.entries(T).map((([e,t])=>({key:e,value:t}))).filter((({key:e})=>!$.includes(e))).filter((({value:e})=>(0,v.px)(e.behaviors||[])&&!e.deprecated)).sort(((e,t)=>e.value.name.localeCompare(t.value.name)))),[T,$]),X=(0,l.useMemo)((()=>{const e={};return Q.forEach((t=>{const i=t.value.category||y;e[i]||(e[i]=[]),e[i].push(t)})),e}),[Q]),Z=(0,l.useMemo)((()=>Object.keys(X).sort(((e,t)=>e===y?1:t===y?-1:e.localeCompare(t)))),[X]),ee=(0,l.useMemo)((()=>{const e={};return Q.forEach((t=>{(t.value.tags||[]).forEach((i=>{e[i]||(e[i]=[]),e[i].push(t)}))})),e}),[Q]),te=(0,l.useMemo)((()=>Object.keys(ee).sort(((e,t)=>e.localeCompare(t))).filter((e=>-1===Y.indexOf(e)))),[ee]),ie=(0,l.useMemo)((()=>Q.sort(((e,t)=>e.value.name.localeCompare(t.value.name)))),[Q]),[ne,ae]=(0,l.useState)((()=>(null==J?void 0:J.category)||U)),[le,re]=(0,l.useState)((()=>null!=J&&J.category?n.Category:n.Featured)),oe=(0,l.useMemo)((()=>new r.A(Q,{ignoreLocation:!0,threshold:.3,keys:[{name:"value.name",weight:4},{name:"value.tags",weight:2},"value.description"]})),[Q]),se=(0,l.useMemo)((()=>""===R.trim()?[]:oe.search(R).map((e=>e.item)).sort(((e,t)=>{var i,n;const a=null==(i=e.value)?void 0:i.label,l=null==(n=t.value)?void 0:n.label,r=a&&p.l7[a]?p.l7[a].weight:0;return(l&&p.l7[l]?p.l7[l].weight:0)-r}))),[R,oe]),de=(0,l.useCallback)((()=>{W(!0)}),[]),ce=(0,l.useCallback)((e=>j(e.target.value)),[]),me=(0,l.useCallback)((()=>{W(!1),j(""),E.current.blur()}),[]),pe=(0,l.useCallback)(((e,t)=>{_&&me(),ae(e),re(t);const i=J&&K(J,e);e===ne||i||s(null)}),[me,_,ne,J,s]),ue=(0,l.useMemo)((()=>({[n.Category]:{title:(0,d.t)("Category"),icon:(0,a.Y)(b.F.Category,{iconSize:"m"}),selectors:Z},[n.Tags]:{title:(0,d.t)("Tags"),icon:(0,a.Y)(b.F.NumberOutlined,{iconSize:"m"}),selectors:te}})),[Z,te]);return(0,a.FD)(w,{className:z,isSelectedVizMetadata:Boolean(J),children:[(0,a.FD)(A,{"aria-label":(0,d.t)("Choose chart type"),role:"tablist",children:[(0,a.Y)(L,{css:({sizeUnit:e})=>m.AH`
              margin: ${2*e}px;
              margin-bottom: 0;
            `,sectionId:n.AllCharts,selector:C,icon:(0,a.Y)(b.F.Ballot,{iconSize:"m"}),isSelected:!q&&C===ne&&n.AllCharts===le,onClick:pe}),(0,a.Y)(L,{css:({sizeUnit:e})=>m.AH`
              margin: ${2*e}px;
              margin-bottom: 0;
            `,sectionId:n.Featured,selector:U,icon:(0,a.Y)(b.F.FireOutlined,{iconSize:"m"}),isSelected:!q&&U===ne&&n.Featured===le,onClick:pe}),(0,a.Y)(u.S,{expandIconPosition:"end",ghost:!0,defaultActiveKey:n.Category,items:Object.keys(ue).map((e=>{const t=ue[e];return{key:e,label:(0,a.Y)("span",{className:"header",children:t.title}),children:(0,a.Y)(a.FK,{children:t.selectors.map((i=>(0,a.Y)(L,{selector:i,sectionId:e,icon:t.icon,isSelected:!q&&i===ne&&e===le,onClick:pe},i)))})}}))})]}),(0,a.Y)(I,{children:(0,a.Y)(h.A,{type:"text",ref:E,value:R,placeholder:(0,d.t)("Search all charts"),onChange:ce,onFocus:de,"data-test":`${k}__search-input`,prefix:(0,a.Y)(M,{children:(0,a.Y)(b.F.SearchOutlined,{iconSize:"m"})}),suffix:(0,a.Y)(M,{children:R&&(0,a.Y)(b.F.CloseOutlined,{iconSize:"m",onClick:me})})})}),(0,a.Y)(F,{children:(0,a.Y)(G,{vizEntries:q?se:ne===C&&le===n.AllCharts?ie:ne===U&&le===n.Featured&&ee[U]?ee[U]:le===n.Category&&X[ne]?X[ne]:le===n.Tags&&ee[ne]?ee[ne]:[],selectedViz:o,setSelectedViz:s,onDoubleClick:c})}),J?(0,a.Y)("div",{css:e=>[D(e),O(e)],children:(0,a.FD)(a.FK,{children:[(0,a.FD)(S,{css:m.AH`
                grid-area: viz-name;
                position: relative;
              `,children:[null==J?void 0:J.name,(null==J?void 0:J.label)&&(0,a.Y)(g.m,{id:"viz-badge-tooltip",placement:"top",title:null!=(t=J.labelExplanation)?t:p.HE[J.label],children:(0,a.Y)(V,{children:(0,a.Y)(P,{children:(0,a.Y)("div",{children:(0,d.t)(J.label)})})})})]}),(0,a.Y)(H,{children:null==J?void 0:J.tags.map((e=>(0,a.Y)(x.JU,{css:({sizeUnit:e})=>m.AH`
                    margin-bottom: ${2*e}px;
                  `,children:e},e)))}),(0,a.Y)(N,{children:(null==J?void 0:J.description)||(0,d.t)("No description available.")}),(0,a.Y)(S,{css:m.AH`
                grid-area: examples-header;
              `,children:(0,d.t)("Examples")}),(0,a.Y)(B,{children:(null!=J&&null!=(i=J.exampleGallery)&&i.length?J.exampleGallery:[{url:null==J?void 0:J.thumbnail,caption:null==J?void 0:J.name}]).map((e=>(0,a.Y)("img",{src:e.url,alt:e.caption,title:e.caption},e.url)))})]})}):null]})}}}]);