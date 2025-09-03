"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[9915],{11188:(e,t,r)=>{r.d(t,{A:()=>u});var a=r(2445),i=r(96540),o=r(72234),s=r(95579),n=r(42944),l=r(38380),c=r(73135);const d=o.I4.div`
  position: relative;
  margin-top: -24px;

  &:hover {
    .copy-button {
      visibility: visible;
    }
  }

  .copy-button {
    position: absolute;
    top: 40px;
    right: 16px;
    z-index: 10;
    visibility: hidden;
    margin: -4px;
    padding: 4px;
    background: ${({theme:e})=>e.colors.grayscale.light4};
    border-radius: ${({theme:e})=>e.borderRadius}px;
    color: ${({theme:e})=>e.colors.grayscale.base};
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: ${({theme:e})=>e.colors.grayscale.light2};
      color: ${({theme:e})=>e.colors.grayscale.dark1};
    }

    &:focus {
      visibility: visible;
      outline: 2px solid ${({theme:e})=>e.colors.primary.base};
      outline-offset: 2px;
    }
  }
`;function u({addDangerToast:e,addSuccessToast:t,children:r,language:o,...u}){function h(r){(0,c.A)((()=>Promise.resolve(r))).then((()=>{t&&t((0,s.t)("Code Copied!"))})).catch((()=>{e&&e((0,s.t)("Sorry, your browser does not support copying."))}))}return(0,i.useEffect)((()=>{(0,n.Fq)([o])}),[o]),(0,a.FD)(d,{children:[(0,a.Y)(l.F.CopyOutlined,{className:"copy-button",tabIndex:0,role:"button","aria-label":(0,s.t)("Copy code to clipboard"),onClick:e=>{e.preventDefault(),e.stopPropagation(),e.currentTarget.blur(),h(r)},onKeyDown:e=>{"Enter"!==e.key&&" "!==e.key||(e.preventDefault(),h(r))}}),(0,a.Y)(n.Ay,{language:o,...u,children:r})]})}},14318:(e,t,r)=>{r.d(t,{A:()=>i});var a=r(96540);function i({queries:e,fetchData:t,currentQueryId:r}){const i=e.findIndex((e=>e.id===r)),[o,s]=(0,a.useState)(i),[n,l]=(0,a.useState)(!1),[c,d]=(0,a.useState)(!1);function u(){l(0===o),d(o===e.length-1)}function h(r){const a=o+(r?-1:1);a>=0&&a<e.length&&(t(e[a].id),s(a),u())}return(0,a.useEffect)((()=>{u()})),{handleKeyPress:function(t){o>=0&&o<e.length&&("ArrowDown"===t.key||"k"===t.key?(t.preventDefault(),h(!1)):"ArrowUp"!==t.key&&"j"!==t.key||(t.preventDefault(),h(!0)))},handleDataChange:h,disablePrevious:n,disableNext:c}}},52825:(e,t,r)=>{r.r(t),r.d(t,{default:()=>Z});var a=r(2445),i=r(96540),o=r(61574),s=r(71519),n=r(72234),l=r(95579),c=r(35742),d=r(69108),u=r(17437),h=r(30703),p=r(5261),m=r(50500),b=r(51713),g=r(82537),y=r(97470),f=r(20900),v=r(93514),S=r(44344),q=r(42944),x=r(27023),k=r(23193),H=r(38380),w=r(46942),D=r.n(w),C=r(84335),F=r(15509),$=r(11188),Y=r(14318);const T=n.I4.div`
  color: ${({theme:e})=>e.colors.primary.light2};
  font-size: ${({theme:e})=>e.fontSizeSM}px;
  margin-bottom: 0;
`,z=n.I4.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
  font-size: ${({theme:e})=>e.fontSize}px;
  padding: 4px 0 24px 0;
`,A=n.I4.div`
  margin: 0 0 ${({theme:e})=>6*e.sizeUnit}px 0;
`,I=n.I4.div`
  display: inline;
  font-size: ${({theme:e})=>e.fontSizeSM}px;
  padding: ${({theme:e})=>2*e.sizeUnit}px
    ${({theme:e})=>4*e.sizeUnit}px;
  margin-right: ${({theme:e})=>4*e.sizeUnit}px;
  color: ${({theme:e})=>e.colorPrimaryText};

  &.active,
  &:focus,
  &:hover {
    background: ${({theme:e})=>e.colors.primary.light4};
    border-bottom: none;
    border-radius: ${({theme:e})=>e.borderRadius}px;
    margin-bottom: ${({theme:e})=>2*e.sizeUnit}px;
  }

  &:hover:not(.active) {
    background: ${({theme:e})=>e.colors.primary.light5};
  }
`,U=(0,n.I4)(C.aF)`
  .ant-modal-body {
    padding: ${({theme:e})=>6*e.sizeUnit}px;
  }
`,N=(0,p.Ay)((function({onHide:e,openInSqlLab:t,queries:r,query:o,fetchData:s,show:n,addDangerToast:c,addSuccessToast:d}){const{handleKeyPress:u,handleDataChange:h,disablePrevious:p,disableNext:m}=(0,Y.A)({queries:r,currentQueryId:o.id,fetchData:s}),[b,g]=(0,i.useState)("user"),{id:y,sql:f,executed_sql:v}=o;return(0,a.Y)("div",{role:"none",onKeyUp:u,children:(0,a.FD)(U,{onHide:e,show:n,title:(0,l.t)("Query preview"),footer:(0,a.FD)(a.FK,{children:[(0,a.Y)(F.$,{"data-test":"previous-query",disabled:p,onClick:()=>h(!0),children:(0,l.t)("Previous")},"previous-query"),(0,a.Y)(F.$,{"data-test":"next-query",disabled:m,onClick:()=>h(!1),children:(0,l.t)("Next")},"next-query"),(0,a.Y)(F.$,{"data-test":"open-in-sql-lab",buttonStyle:"primary",onClick:()=>t(y),children:(0,l.t)("Open in SQL Lab")},"open-in-sql-lab")]}),children:[(0,a.Y)(T,{children:(0,l.t)("Tab name")}),(0,a.Y)(z,{children:o.tab_name}),(0,a.FD)(A,{children:[(0,a.Y)(I,{role:"button","data-test":"toggle-user-sql",className:D()({active:"user"===b}),onClick:()=>g("user"),children:(0,l.t)("User query")}),(0,a.Y)(I,{role:"button","data-test":"toggle-executed-sql",className:D()({active:"executed"===b}),onClick:()=>g("executed"),children:(0,l.t)("Executed query")})]}),(0,a.Y)($.A,{addDangerToast:c,addSuccessToast:d,language:"sql",children:("user"===b?f:v)||""})]})})}));var R=r(95272),Q=r(25106),L=r(95070);const P=(0,n.I4)(S.uO)`
  table .ant-table-cell {
    vertical-align: top;
  }
`,E=(0,n.I4)(q.Ay)`
  height: ${({theme:e})=>26*e.sizeUnit}px;
  overflow: hidden !important; /* needed to override inline styles */
  text-overflow: ellipsis;
  white-space: nowrap;

  /* Ensure the syntax highlighter content respects the container constraints */
  & > div {
    height: 100%;
    overflow: hidden;
  }

  pre {
    height: 100% !important;
    overflow: hidden !important;
    margin: 0 !important;
  }
`,O=n.I4.div`
  .count {
    margin-left: 5px;
    color: ${({theme:e})=>e.colorPrimary};
    text-decoration: underline;
    cursor: pointer;
  }
`,_=n.I4.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
`,K=(0,n.I4)(g.JU)`
  text-align: left;
  font-family: ${({theme:e})=>e.fontFamilyCode};
`,Z=(0,p.Ay)((function({addDangerToast:e}){const{state:{loading:t,resourceCount:r,resourceCollection:p},fetchData:g}=(0,m.RU)("query",(0,l.t)("Query history"),e,!1),[w,D]=(0,i.useState)(),C=(0,n.DP)(),F=(0,o.W6)();(0,i.useEffect)((()=>{(0,q.Fq)(["sql"])}),[]);const $=(0,i.useCallback)((t=>{c.A.get({endpoint:`/api/v1/query/${t}`}).then((({json:e={}})=>{D({...e.result})}),(0,h.JF)((t=>e((0,l.t)("There was an issue previewing the selected query. %s",t)))))}),[e]),Y={activeChild:"Query history",...v.F},T=[{id:k.H.StartTime,desc:!0}],z=(0,i.useMemo)((()=>[{Cell:({row:{original:{status:e}}})=>{const t={name:null,label:""};return e===d.kZ.Success?(t.name=(0,a.Y)(H.F.CheckOutlined,{iconSize:"m",iconColor:C.colorSuccess,css:u.AH`
                  vertical-align: -webkit-baseline-middle;
                `}),t.label=(0,l.t)("Success")):e===d.kZ.Failed||e===d.kZ.Stopped?(t.name=(0,a.Y)(H.F.CloseOutlined,{iconSize:"xs",iconColor:e===d.kZ.Failed?C.colorError:C.colors.grayscale.base}),t.label=(0,l.t)("Failed")):e===d.kZ.Running?(t.name=(0,a.Y)(H.F.Running,{iconColor:C.colorPrimary}),t.label=(0,l.t)("Running")):e===d.kZ.TimedOut?(t.name=(0,a.Y)(H.F.CircleSolid,{iconColor:C.colors.grayscale.light1}),t.label=(0,l.t)("Offline")):e!==d.kZ.Scheduled&&e!==d.kZ.Pending||(t.name=(0,a.Y)(H.F.Queued,{}),t.label=(0,l.t)("Scheduled")),(0,a.Y)(y.m,{title:t.label,placement:"bottom",children:(0,a.Y)("span",{children:t.name})})},accessor:k.H.Status,size:"xs",disableSortBy:!0,id:k.H.Status},{accessor:k.H.StartTime,Header:(0,l.t)("Time"),size:"xl",Cell:({row:{original:{start_time:e}}})=>{const t=L.XV.utc(e).local().format(x.QU).split(" ");return(0,a.FD)(a.FK,{children:[t[0]," ",(0,a.Y)("br",{}),t[1]]})},id:k.H.StartTime},{Header:(0,l.t)("Duration"),size:"xl",Cell:({row:{original:{status:e,start_time:t,end_time:r}}})=>{const i=e===d.kZ.Failed?"danger":e,o=r?(0,L.XV)(L.XV.utc(r-t)).format(x.os):"00:00:00.000";return(0,a.Y)(K,{type:i,role:"timer",children:o})},id:"duration"},{accessor:k.H.TabName,Header:(0,l.t)("Tab name"),size:"xl",id:k.H.TabName},{accessor:k.H.DatabaseName,Header:(0,l.t)("Database"),size:"xl",id:k.H.DatabaseName},{accessor:k.H.Database,hidden:!0,id:k.H.Database},{accessor:k.H.Schema,Header:(0,l.t)("Schema"),size:"xl",id:k.H.Schema},{Cell:({row:{original:{sql_tables:e=[]}}})=>{const t=e.map((e=>e.table)),r=t.length>0?t.shift():"";return t.length?(0,a.FD)(O,{children:[(0,a.Y)("span",{children:r}),(0,a.Y)(f.A,{placement:"right",title:(0,l.t)("TABLES"),trigger:"click",content:(0,a.Y)(a.FK,{children:t.map((e=>(0,a.Y)(_,{children:e},e)))}),children:(0,a.FD)("span",{className:"count",children:["(+",t.length,")"]})})]}):r},accessor:k.H.SqlTables,Header:(0,l.t)("Tables"),size:"xl",disableSortBy:!0,id:k.H.SqlTables},{accessor:k.H.UserFirstName,Header:(0,l.t)("User"),size:"xl",Cell:({row:{original:{user:e}}})=>(0,Q.A)(e),id:k.H.UserFirstName},{accessor:k.H.User,hidden:!0,id:k.H.User},{accessor:k.H.Rows,Header:(0,l.t)("Rows"),size:"md",id:k.H.Rows},{accessor:k.H.Sql,Header:(0,l.t)("SQL"),Cell:({row:{original:e,id:t}})=>(0,a.Y)("div",{tabIndex:0,role:"button","data-test":`open-sql-preview-${t}`,onClick:()=>D(e),onKeyDown:t=>{"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),D(e))},style:{cursor:"pointer"},children:(0,a.Y)(E,{language:"sql",customStyle:{cursor:"pointer",userSelect:"none"},children:(0,h.s4)(e.sql,4)})}),id:k.H.Sql},{Header:(0,l.t)("Actions"),id:"actions",disableSortBy:!0,Cell:({row:{original:{id:e}}})=>(0,a.Y)(y.m,{title:(0,l.t)("Open query in SQL Lab"),placement:"bottom",children:(0,a.Y)(s.N_,{to:`/sqllab?queryId=${e}`,children:(0,a.Y)(H.F.Full,{iconSize:"l"})})})}]),[C]),A=(0,i.useMemo)((()=>[{Header:(0,l.t)("Database"),key:"database",id:"database",input:"select",operator:S.c0.RelationOneMany,unfilteredLabel:(0,l.t)("All"),fetchSelects:(0,h.u1)("query","database",(0,h.JF)((t=>e((0,l.t)("An error occurred while fetching database values: %s",t))))),paginate:!0},{Header:(0,l.t)("State"),key:"state",id:"status",input:"select",operator:S.c0.Equals,unfilteredLabel:"All",fetchSelects:(0,h.$C)("query","status",(0,h.JF)((t=>e((0,l.t)("An error occurred while fetching schema values: %s",t))))),paginate:!0},{Header:(0,l.t)("User"),key:"user",id:"user",input:"select",operator:S.c0.RelationOneMany,unfilteredLabel:"All",fetchSelects:(0,h.u1)("query","user",(0,h.JF)((t=>e((0,l.t)("An error occurred while fetching user values: %s",t))))),paginate:!0},{Header:(0,l.t)("Time range"),key:"start_time",id:"start_time",input:"datetime_range",operator:S.c0.Between},{Header:(0,l.t)("Search by query text"),key:"sql",id:"sql",input:"search",operator:S.c0.Contains}]),[e]);return(0,a.FD)(a.FK,{children:[(0,a.Y)(b.A,{...Y}),w&&(0,a.Y)(N,{onHide:()=>D(void 0),query:w,queries:p,fetchData:$,openInSqlLab:e=>F.push(`/sqllab?queryId=${e}`),show:!0}),(0,a.Y)(P,{className:"query-history-list-view",columns:z,count:r,data:p,fetchData:g,filters:A,initialSort:T,loading:t,pageSize:25,highlightRowId:null==w?void 0:w.id,refreshData:()=>{},addDangerToast:e,addSuccessToast:R.WR})]})}))},93514:(e,t,r)=>{r.d(t,{F:()=>i});var a=r(95579);const i={name:(0,a.t)("SQL"),tabs:[{name:"Saved queries",label:(0,a.t)("Saved queries"),url:"/savedqueryview/list/",usesRouter:!0},{name:"Query history",label:(0,a.t)("Query history"),url:"/sqllab/history/",usesRouter:!0}]}}}]);