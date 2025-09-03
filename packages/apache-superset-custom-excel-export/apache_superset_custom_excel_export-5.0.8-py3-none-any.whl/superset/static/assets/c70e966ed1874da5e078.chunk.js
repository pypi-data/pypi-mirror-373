"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[7889],{21671:(e,n,t)=>{function l(e,n){let t;if(void 0===n)for(const n of e)null!=n&&(t<n||void 0===t&&n>=n)&&(t=n);else{let l=-1;for(let o of e)null!=(o=n(o,++l,e))&&(t<o||void 0===t&&o>=o)&&(t=o)}return t}t.d(n,{A:()=>l})},31656:(e,n,t)=>{t.d(n,{A:()=>s});var l=t(58168),o=t(96540);const r={icon:{tag:"svg",attrs:{viewBox:"64 64 896 896",focusable:"false"},children:[{tag:"path",attrs:{d:"M868 545.5L536.1 163a31.96 31.96 0 00-48.3 0L156 545.5a7.97 7.97 0 006 13.2h81c4.6 0 9-2 12.1-5.5L474 300.9V864c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V300.9l218.9 252.3c3 3.5 7.4 5.5 12.1 5.5h81c6.8 0 10.5-8 6-13.2z"}}]},name:"arrow-up",theme:"outlined"};var i=t(12226),a=function(e,n){return o.createElement(i.A,(0,l.A)({},e,{ref:n,icon:r}))};const s=o.forwardRef(a)},61573:(e,n,t)=>{function l(e,n){let t,l;if(void 0===n)for(const n of e)null!=n&&(void 0===t?n>=n&&(t=l=n):(t>n&&(t=n),l<n&&(l=n)));else{let o=-1;for(let r of e)null!=(r=n(r,++o,e))&&(void 0===t?r>=r&&(t=l=r):(t>r&&(t=r),l<r&&(l=r)))}return[t,l]}t.d(n,{A:()=>l})},75163:(e,n,t)=>{t.d(n,{A:()=>s});var l=t(58168),o=t(96540);const r={icon:{tag:"svg",attrs:{viewBox:"64 64 896 896",focusable:"false"},children:[{tag:"path",attrs:{d:"M862 465.3h-81c-4.6 0-9 2-12.1 5.5L550 723.1V160c0-4.4-3.6-8-8-8h-60c-4.4 0-8 3.6-8 8v563.1L255.1 470.8c-3-3.5-7.4-5.5-12.1-5.5h-81c-6.8 0-10.5 8.1-6 13.2L487.9 861a31.96 31.96 0 0048.3 0L868 478.5c4.5-5.2.8-13.2-6-13.2z"}}]},name:"arrow-down",theme:"outlined"};var i=t(12226),a=function(e,n){return o.createElement(i.A,(0,l.A)({},e,{ref:n,icon:r}))};const s=o.forwardRef(a)},77889:(e,n,t)=>{t.r(n),t.d(n,{default:()=>Ie});var l=t(2404),o=t.n(l),r=t(2445),i=t(87903),a=t(95579),s=t(7349),c=t(96540),u=t(38221),d=t.n(u),g=t(80346),h=t(66875),p=t(42877),m=t(17451),v=t(50329),f=t(68e3),C=t(97),b=t(71781),x=t(72234),w=t(17437);const y=x.I4.div`
  ${({theme:e})=>`\n    display: flex;\n    width: 100%;\n\n    .three-dots-menu {\n      align-self: center;\n      margin-left: ${e.sizeUnit}px;\n      cursor: pointer;\n      padding: ${e.sizeUnit/2}px;\n      border-radius: ${e.borderRadius}px;\n      margin-top: ${.75*e.sizeUnit}px;\n    }\n  `}
`,$=x.I4.div`
  ${({theme:e})=>`\n    width: 100%;\n    display: flex;\n    align-items: center;\n    cursor: pointer;\n    padding: 0 ${2*e.sizeUnit}px;\n    overflow: hidden;\n  `}
`,S=x.I4.span`
  ${({theme:e})=>`\n    font-weight: ${e.fontWeightStrong};\n    white-space: nowrap;\n    overflow: hidden;\n    text-overflow: ellipsis;\n    display: block;\n    max-width: 100%;\n  `}
`,F=x.I4.div`
  ${({theme:e})=>`\n    display: flex;\n    align-items: center;\n    margin-left: ${2*e.sizeUnit}px;\n  `}
`,k=x.I4.div`
  align-self: flex-end;
  margin-left: auto;
  cursor: pointer;

  padding: 3px 4px;
  overflow: hidden;
  cursor: pointer;
  border-radius: 4px;

  ${({isFilterActive:e})=>e&&w.AH`
      background: linear-gradient(
        var(--ag-icon-button-active-background-color),
        var(--ag-icon-button-active-background-color)
      );
      ::after {
        background-color: var(--ag-accent-color);
        border-radius: 50%;
        content: '';
        height: 6px;
        position: absolute;
        right: 4px;
        width: 6px;
      }
    `}

  svg {
    ${({isFilterActive:e})=>e&&w.AH`
        clip-path: path('M8,0C8,4.415 11.585,8 16,8L16,16L0,16L0,0L8,0Z');
        color: var(--ag-icon-button-active-color);
      `}

    :hover {
      ${({isFilterActive:e})=>!e&&w.AH`
          background-color: var(--ag-icon-button-hover-background-color);
          box-shadow: 0 0 0 var(--ag-icon-button-background-spread)
            var(--ag-icon-button-hover-background-color);
          color: var(--ag-icon-button-hover-color);
          border-radius: var(--ag-icon-button-border-radius);
        `}
    }
  }
`,A=x.I4.div`
  ${({theme:e})=>`\n    min-width: ${45*e.sizeUnit}px;\n    padding: ${e.sizeUnit}px 0;\n\n    .menu-item {\n      padding: ${2*e.sizeUnit}px ${4*e.sizeUnit}px;\n      cursor: pointer;\n      display: flex;\n      align-items: center;\n      gap: ${2*e.sizeUnit}px;\n\n      &:hover {\n        background-color: ${e.colors.primary.light4};\n      }\n    }\n\n    .menu-divider {\n      height: 1px;\n      background-color: ${e.colors.grayscale.light2};\n      margin: ${e.sizeUnit}px 0;\n    }\n  `}
`,P=x.I4.div`
  position: relative;
  display: inline-block;
`,z=x.I4.div`
  ${({theme:e})=>`\n      position: fixed;\n      box-shadow: var(--ag-menu-shadow);\n      border-radius: ${e.sizeUnit}px;\n      z-index: 99;\n      min-width: ${50*e.sizeUnit}px;\n      background: var(--ag-menu-background-color);\n      border: var(--ag-menu-border);\n      box-shadow: var(--ag-menu-shadow);\n      color: var(--ag-menu-text-color);\n\n    `}
`,M=x.I4.div`
  ${({theme:e})=>`\n    border: 1px solid ${e.colors.grayscale.light2};\n    display: flex;\n    align-items: center;\n    justify-content: flex-end;\n    padding: ${2*e.sizeUnit}px ${4*e.sizeUnit}px;\n    border-top: 1px solid ${e.colors.grayscale.light2};\n    font-size: ${e.fontSize}px;\n    color: ${e.colorTextBase};\n    transform: translateY(-${e.sizeUnit}px);\n    background: ${e.colorBgBase};\n  `}
`,N=x.I4.div`
  ${({theme:e})=>`\n    position: relative;\n    margin-left: ${2*e.sizeUnit}px;\n    display: inline-block;\n    min-width: ${17*e.sizeUnit}px;\n    overflow: hidden;\n  `}
`,Y=x.I4.span`
  ${({theme:e})=>`\n    margin: 0 ${6*e.sizeUnit}px;\n    span {\n      font-weight: ${e.fontWeightStrong};\n    }\n  `}
`,D=x.I4.span`
  ${({theme:e})=>`\n    span {\n      font-weight: ${e.fontWeightStrong};\n    }\n  `}
`,I=x.I4.div`
  ${({theme:e})=>`\n    display: flex;\n    gap: ${3*e.sizeUnit}px;\n  `}
`,T=x.I4.div`
  ${({theme:e,disabled:n})=>`\n    cursor: ${n?"not-allowed":"pointer"};\n    display: flex;\n    align-items: center;\n    justify-content: center;\n\n    svg {\n      height: ${3*e.sizeUnit}px;\n      width: ${3*e.sizeUnit}px;\n      fill: ${n?e.colors.grayscale.light1:e.colors.grayscale.dark2};\n    }\n  `}
`,L=(0,x.I4)(b.A)`
  ${({theme:e})=>`\n    width: ${30*e.sizeUnit}px;\n    margin-right: ${2*e.sizeUnit}px;\n  `}
`,R=x.I4.div`
  max-width: 242px;
  ${({theme:e})=>`\n    padding: 0 ${2*e.sizeUnit}px;\n    color: ${e.colors.grayscale.base};\n    font-size: ${e.fontSizeSM}px;\n  `}
`,U=x.I4.span`
  ${({theme:e})=>`\n    color: ${e.colors.grayscale.dark2};\n  `}
`,B=x.I4.span`
  ${({theme:e})=>`\n    float: right;\n    font-size: ${e.fontSizeSM}px;\n  `}
`,E=x.I4.div`
  ${({theme:e})=>`\n    display: flex;\n    align-items: center;\n    gap: ${e.sizeUnit}px;\n  `}
`,H=x.I4.div`
  ${({theme:e})=>`\n    font-weight: ${e.fontWeightStrong};\n  `}
`,O=x.I4.div`
  ${({theme:e,height:n})=>w.AH`
    height: ${n}px;

    --ag-background-color: ${e.colorBgBase};
    --ag-foreground-color: ${e.colorText};
    --ag-header-background-color: ${e.colorBgBase};
    --ag-header-foreground-color: ${e.colorText};

    .dt-is-filter {
      cursor: pointer;
      :hover {
        background-color: ${e.colorPrimaryBgHover};
      }
    }

    .dt-is-active-filter {
      background: ${e.colors.primary.light3};
      :hover {
        background-color: ${e.colorPrimaryBgHover};
      }
    }

    .dt-truncate-cell {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .dt-truncate-cell:hover {
      overflow: visible;
      white-space: normal;
      height: auto;
    }

    .ag-container {
      border-radius: 0px;
      border: var(--ag-wrapper-border);
    }

    .ag-input-wrapper {
      ::before {
        z-index: 100;
      }
    }

    .filter-popover {
      z-index: 1 !important;
    }

    .search-container {
      display: flex;
      justify-content: flex-end;
      margin-bottom: ${4*e.sizeUnit}px;
    }

    .dropdown-controls-container {
      display: flex;
      justify-content: flex-end;
    }

    .time-comparison-dropdown {
      display: flex;
      padding-right: ${4*e.sizeUnit}px;
      padding-top: ${1.75*e.sizeUnit}px;
      height: fit-content;
    }

    .ag-header,
    .ag-row,
    .ag-spanned-row {
      font-size: ${e.fontSizeSM}px;
      font-weight: ${e.fontWeightStrong};
    }

    .ag-root-wrapper {
      border-radius: 0px;
    }
    .search-by-text-container {
      display: flex;
      align-items: center;
    }

    .search-by-text {
      margin-right: ${2*e.sizeUnit}px;
    }

    .ant-popover-inner {
      padding: 0px;
    }

    .input-container {
      margin-left: auto;
    }

    .input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      overflow: visible;
    }

    .input-wrapper svg {
      pointer-events: none;
      transform: translate(${7*e.sizeUnit}px, ${e.sizeUnit/2}px);
      color: ${e.colors.grayscale.base};
    }

    .input-wrapper input {
      color: ${e.colorText};
      font-size: ${e.fontSizeSM}px;
      padding: ${1.5*e.sizeUnit}px ${3*e.sizeUnit}px
        ${1.5*e.sizeUnit}px ${8*e.sizeUnit}px;
      line-height: 1.8;
      border-radius: ${e.borderRadius}px;
      border: 1px solid ${e.colors.grayscale.light2};
      background-color: transparent;
      outline: none;

      &:focus {
        border-color: ${e.colors.primary.base};
      }

      &::placeholder {
        color: ${e.colors.grayscale.light1};
      }
    }
  `}
`,G=({currentPage:e=0,pageSize:n=10,totalRows:t=0,pageSizeOptions:l=[10,20,50,100,200],onServerPaginationChange:o=()=>{},onServerPageSizeChange:i=()=>{},sliceId:s})=>{const c=Math.ceil(t/n),u=e*n+1,d=Math.min((e+1)*n,t),g=l.map((e=>({value:e,label:e})));return(0,r.FD)(M,{children:[(0,r.Y)("span",{children:(0,a.t)("Page Size:")}),(0,r.Y)(N,{children:(0,r.Y)(b.A,{value:`${n}`,options:g,onChange:e=>{i(Number(e))},getPopupContainer:()=>document.getElementById(`chart-id-${s}`)})}),(0,r.FD)(Y,{children:[(0,r.Y)("span",{children:u})," ",(0,a.t)("to")," ",(0,r.Y)("span",{children:d})," ",(0,a.t)("of")," ",(0,r.Y)("span",{children:t})]}),(0,r.FD)(I,{children:[(0,r.Y)(T,{onClick:(h=0===e,()=>{h||o(0,n)}),disabled:0===e,children:(0,r.Y)(m.A,{})}),(0,r.Y)(T,{onClick:(t=>()=>{t||o(e-1,n)})(0===e),disabled:0===e,children:(0,r.Y)(v.A,{})}),(0,r.FD)(D,{children:[(0,a.t)("Page")," ",(0,r.Y)("span",{children:e+1})," ",(0,a.t)("of")," ",(0,r.Y)("span",{children:c})]}),(0,r.Y)(T,{onClick:(t=>()=>{t||o(e+1,n)})(!!(e>=c-1)),disabled:e>=c-1,children:(0,r.Y)(f.A,{})}),(0,r.Y)(T,{onClick:(e=>()=>{e||o(c-1,n)})(!!(e>=c-1)),disabled:e>=c-1,children:(0,r.Y)(C.A,{})})]})]});var h},V=function({value:e,onChange:n,searchOptions:t}){var l,o;return(0,r.Y)(L,{className:"search-select",value:e||(null!=(l=null==t||null==(o=t[0])?void 0:o.value)?l:""),options:t,onChange:n})},W=e=>{var n,t;return Array.isArray(e)&&e.length>0?[{colId:null==(n=e[0])?void 0:n.id,sort:null!=(t=e[0])&&t.desc?"desc":"asc"}]:[]};var q=t(95153);g.syG.registerModules([g.JKr,g.Q90]);const j=new Map,_=(0,c.memo)((({gridHeight:e,data:n=[],colDefsFromProps:t,includeSearch:l,allowRearrangeColumns:i,pagination:s,pageSize:u,serverPagination:m,rowCount:v,onServerPaginationChange:f,serverPaginationData:C,onServerPageSizeChange:b,searchOptions:x,onSearchColChange:w,onSearchChange:y,onSortChange:$,id:S,percentMetrics:F,serverPageLength:k,hasServerPageLengthChanged:A,handleCrossFilter:P,isActiveFilterValue:z,renderTimeComparisonDropdown:M,cleanedTotals:N,showTotals:Y,width:D})=>{const I=(0,c.useRef)(null),T=(0,c.useRef)(null),L=(0,c.useMemo)((()=>n),[n]),R=(0,c.useRef)(null),U=`search-${S}`,B={...m&&{sort:{sortModel:W((null==C?void 0:C.sortBy)||[])}}},E=(0,c.useMemo)((()=>({flex:1,filter:!0,enableRowGroup:!0,enableValue:!0,sortable:!0,resizable:!0,minWidth:100})),[]),H=(0,c.useMemo)((()=>({height:e,width:D})),[e,D]),[O,_]=(0,c.useState)(),[K,J]=(0,c.useState)((null==C?void 0:C.searchText)||""),Q=(0,c.useMemo)((()=>d()((e=>{y(e)}),500)),[y]);(0,c.useEffect)((()=>()=>{Q.cancel()}),[Q]),(0,c.useEffect)((()=>{var e;m&&j.get(U)&&document.activeElement!==T.current&&(null==(e=T.current)||e.focus())}),[K,m,U]);const X=(0,c.useCallback)((()=>{j.set(U,!0)}),[U]),Z=(0,c.useCallback)((()=>{j.set(U,!1)}),[U]),ee=(0,c.useCallback)((({target:{value:e}})=>{m?(J(e),Q(e)):_(e)}),[m,Q,U]),ne=(0,c.useCallback)((e=>{var n,t;((e,n)=>{const t=(({colId:e,sortDir:n,percentMetrics:t,serverPagination:l,gridInitialState:o})=>{var r;if(t.includes(e))return!1;if(!l)return!1;const{colId:i="",sort:a}=(null==o||null==(r=o.sort)||null==(r=r.sortModel)?void 0:r[0])||{};return i!==e||a!==n})({colId:e,sortDir:n,percentMetrics:F,serverPagination:!!m,gridInitialState:B});t&&$(null!=n?[{id:e,key:e,desc:"desc"===n}]:[])})(null==e||null==(n=e.column)?void 0:n.colId,null==e||null==(t=e.column)?void 0:t.sort)}),[m,B,F,$]);return(0,c.useEffect)((()=>{A&&null!=C&&C.pageSize&&!o()(null==C?void 0:C.pageSize,k)&&b(k)}),[A]),(0,r.FD)("div",{className:"ag-theme-quartz",style:H,ref:R,children:[(0,r.FD)("div",{className:"dropdown-controls-container",children:[M&&(0,r.Y)("div",{className:"time-comparison-dropdown",children:M()}),l&&(0,r.FD)("div",{className:"search-container",children:[m&&(0,r.FD)("div",{className:"search-by-text-container",children:[(0,r.Y)("span",{className:"search-by-text",children:" Search by :"}),(0,r.Y)(V,{onChange:w,searchOptions:x,value:(null==C?void 0:C.searchColumn)||""})]}),(0,r.Y)("div",{className:"input-wrapper",children:(0,r.FD)("div",{className:"input-container",children:[(0,r.Y)(p.A,{}),(0,r.Y)("input",{ref:T,value:m?K:O||"",type:"text",id:"filter-text-box",placeholder:"Search",onInput:ee,onFocus:X,onBlur:Z})]})})]})]}),(0,r.Y)(h.W6,{ref:I,onGridReady:e=>{e.api.sizeColumnsToFit()},theme:g.zl0,className:"ag-container",rowData:L,headerHeight:36,rowHeight:30,columnDefs:t,defaultColDef:E,onColumnGroupOpened:e=>e.api.sizeColumnsToFit(),rowSelection:"multiple",animateRows:!0,onCellClicked:P,initialState:B,suppressAggFuncInHeader:!0,rowGroupPanelShow:"always",enableCellTextSelection:!0,quickFilterText:m?"":O,suppressMovableColumns:!i,pagination:s,paginationPageSize:u,paginationPageSizeSelector:q.xp,suppressDragLeaveHidesColumns:!0,pinnedBottomRowData:Y?[N]:void 0,localeText:{next:(0,a.t)("Next"),previous:(0,a.t)("Previous"),page:(0,a.t)("Page"),more:(0,a.t)("More"),to:(0,a.t)("to"),of:(0,a.t)("of"),first:(0,a.t)("First"),last:(0,a.t)("Last"),loadingOoo:(0,a.t)("Loading..."),selectAll:(0,a.t)("Select All"),searchOoo:(0,a.t)("Search..."),blanks:(0,a.t)("Blanks"),filterOoo:(0,a.t)("Filter"),applyFilter:(0,a.t)("Apply Filter"),equals:(0,a.t)("Equals"),notEqual:(0,a.t)("Not Equal"),lessThan:(0,a.t)("Less Than"),greaterThan:(0,a.t)("Greater Than"),lessThanOrEqual:(0,a.t)("Less Than or Equal"),greaterThanOrEqual:(0,a.t)("Greater Than or Equal"),inRange:(0,a.t)("In Range"),contains:(0,a.t)("Contains"),notContains:(0,a.t)("Not Contains"),startsWith:(0,a.t)("Starts With"),endsWith:(0,a.t)("Ends With"),andCondition:(0,a.t)("AND"),orCondition:(0,a.t)("OR"),group:(0,a.t)("Group"),columns:(0,a.t)("Columns"),filters:(0,a.t)("Filters"),valueColumns:(0,a.t)("Value Columns"),pivotMode:(0,a.t)("Pivot Mode"),groups:(0,a.t)("Groups"),values:(0,a.t)("Values"),pivots:(0,a.t)("Pivots"),toolPanelButton:(0,a.t)("Tool Panel"),pinColumn:(0,a.t)("Pin Column"),valueAggregation:(0,a.t)("Value Aggregation"),autosizeThiscolumn:(0,a.t)("Autosize This Column"),autosizeAllColumns:(0,a.t)("Autosize All Columns"),groupBy:(0,a.t)("Group By"),ungroupBy:(0,a.t)("Ungroup By"),resetColumns:(0,a.t)("Reset Columns"),expandAll:(0,a.t)("Expand All"),collapseAll:(0,a.t)("Collapse All"),toolPanel:(0,a.t)("Tool Panel"),export:(0,a.t)("Export"),csvExport:(0,a.t)("CSV Export"),excelExport:(0,a.t)("Excel Export"),excelXmlExport:(0,a.t)("Excel XML Export"),sum:(0,a.t)("Sum"),min:(0,a.t)("Min"),max:(0,a.t)("Max"),none:(0,a.t)("None"),count:(0,a.t)("Count"),average:(0,a.t)("Average"),copy:(0,a.t)("Copy"),copyWithHeaders:(0,a.t)("Copy with Headers"),paste:(0,a.t)("Paste"),sortAscending:(0,a.t)("Sort Ascending"),sortDescending:(0,a.t)("Sort Descending"),sortUnSort:(0,a.t)("Clear Sort")},context:{onColumnHeaderClicked:ne,initialSortState:W((null==C?void 0:C.sortBy)||[]),isActiveFilterValue:z}}),m&&(0,r.Y)(G,{currentPage:(null==C?void 0:C.currentPage)||0,pageSize:A?k:(null==C?void 0:C.pageSize)||10,totalRows:v||0,pageSizeOptions:[10,20,50,100,200],onServerPaginationChange:f,onServerPageSizeChange:b,sliceId:S})]})}));_.displayName="AgGridDataTable";const K=(0,c.memo)(_);var J=t(31149),Q=t(88603),X=t(87206),Z=t(26067),ee=t(13341),ne=t(14103);const te=({comparisonColumns:e,selectedComparisonColumns:n,onSelectionChange:t})=>{const[l,o]=(0,c.useState)(!1),i=e[0].key;return(0,r.Y)(Q.A,{placement:"bottomRight",visible:l,onVisibleChange:e=>{o(e)},overlay:(0,r.FD)(X.A,{multiple:!0,onClick:e=>{const{key:l}=e;l===i?t([i]):n.includes(i)?t([l]):t(n.includes(l)?n.filter((e=>e!==l)):[...n,l])},onBlur:()=>{3===n.length&&t([e[0].key])},selectedKeys:n,children:[(0,r.Y)(R,{children:(0,a.t)("Select columns that will be displayed in the table. You can multiselect columns.")}),e.map((e=>(0,r.FD)(X.A.Item,{children:[(0,r.Y)(U,{children:e.label}),(0,r.Y)(B,{children:n.includes(e.key)&&(0,r.Y)(Z.A,{})})]},e.key)))]}),trigger:["click"],children:(0,r.FD)("span",{children:[(0,r.Y)(ee.A,{})," ",(0,r.Y)(ne.A,{})]})})};var le=t(21671),oe=t(61573);const re=e=>{const n=e.data[e.colDef.field],t=e.colDef.valueFormatter;if(!n||!t)return null;const l=t({value:n}),o=parseFloat(String(l).replace("%","").trim());return Number.isNaN(o)?null:o},ie=(e,n)=>{const t=new Date(n);if(t.setHours(0,0,0,0),Number.isNaN(null==t?void 0:t.getTime()))return-1;const l=t.getDate(),o=t.getMonth(),r=t.getFullYear(),i=e.getDate(),a=e.getMonth(),s=e.getFullYear();return r<s?-1:r>s?1:o<a?-1:o>a?1:l<i?-1:l>i?1:0},ae=e=>e.isMetric||e.isPercentMetric?q.QH.queryTotal:e.isNumeric?"sum":void 0;var se=t(58642),ce=t(29248),ue=t(97470);const de=(0,a.t)("Show total aggregations of selected metrics. Note that row limit does not apply to the result.");var ge=t(84140);const he=x.I4.div`
  ${()=>"\n    font-weight: bold;\n  "}
`,pe=x.I4.div`
  display: flex;
  background-color: ${({backgroundColor:e})=>e||"transparent"};
  justify-content: ${({align:e})=>e||"left"};
`,me=x.I4.div`
  margin-right: 10px;
  color: ${({arrowColor:e})=>e||"inherit"};
`,ve=x.I4.div`
  position: absolute;
  left: ${({offset:e})=>`${e}%`};
  top: 0;
  height: 100%;
  width: ${({percentage:e})=>`${e}%`};
  background-color: ${({background:e})=>e};
  z-index: 1;
`,fe=e=>{var n;const{value:t,valueFormatted:l,node:o,hasBasicColorFormatters:i,col:a,basicColorFormatters:s,valueRange:c,alignPositiveNegative:u,colorPositiveNegative:d}=e,g=(()=>{const e=(0,x.DP)();return(0,ge.A)(e.colorBgContainer).isDark()})();if("bottom"===(null==o?void 0:o.rowPinned))return(0,r.Y)(he,{children:null!=l?l:t});let h="",p="";var m,v;i&&null!=a&&a.metricName&&(h=null==s||null==(m=s[null==o?void 0:o.rowIndex])||null==(m=m[a.metricName])?void 0:m.mainArrow,p=null==s||null==(v=s[null==o?void 0:o.rowIndex])||null==(v=v[a.metricName])||null==(v=v.arrowColor)?void 0:v.toLowerCase());const f=(null==a||null==(n=a.config)?void 0:n.horizontalAlign)||(null!=a&&a.isNumeric?"right":"left");if(!c)return(0,r.FD)(pe,{align:f,children:[h&&(0,r.Y)(me,{arrowColor:p,children:h}),(0,r.Y)("div",{children:null!=l?l:t})]});const C=function({value:e,valueRange:n,alignPositiveNegative:t}){const[l,o]=n;if(t)return Math.abs(Math.round(e/o*100));const r=Math.abs(Math.max(o,0))+Math.abs(Math.min(l,0));return Math.round(Math.abs(e)/r*100)}({value:t,valueRange:c,alignPositiveNegative:u}),b=function({value:e,valueRange:n,alignPositiveNegative:t}){if(t)return 0;const[l,o]=n,r=Math.abs(Math.max(o,0)),i=Math.abs(Math.min(l,0)),a=r+i;return Math.round(Math.min(i+e,i)/a*100)}({value:t,valueRange:c,alignPositiveNegative:u}),w=function({value:e,colorPositiveNegative:n=!1,isDarkTheme:t=!1}){return n?`rgba(${e<0?150:0},${e>=0?150:0},0,0.2)`:t?"rgba(255,255,255,0.2)":"rgba(0,0,0,0.2)"}({value:t,colorPositiveNegative:d,isDarkTheme:g});return(0,r.FD)("div",{children:[(0,r.Y)(ve,{offset:b,percentage:C,background:w}),null!=l?l:t]})};var Ce=t(31656),be=t(75163);const xe=()=>(0,r.FD)("svg",{width:"16",height:"16",viewBox:"0 0 24 24",fill:"currentColor",children:[(0,r.Y)("rect",{x:"3",y:"6",width:"18",height:"2",rx:"1"}),(0,r.Y)("rect",{x:"6",y:"11",width:"12",height:"2",rx:"1"}),(0,r.Y)("rect",{x:"9",y:"16",width:"6",height:"2",rx:"1"})]}),we=({size:e=14})=>(0,r.FD)("svg",{width:e,height:e,viewBox:"0 0 16 16",fill:"currentColor",xmlns:"http://www.w3.org/2000/svg",children:[(0,r.Y)("circle",{cx:"8",cy:"3",r:"1.2"}),(0,r.Y)("circle",{cx:"8",cy:"8",r:"1.2"}),(0,r.Y)("circle",{cx:"8",cy:"13",r:"1.2"})]}),ye=({content:e,children:n,isOpen:t,onClose:l})=>{const[o,i]=(0,c.useState)({top:0,left:0}),a=(0,c.useRef)(null),s=(0,c.useRef)(null);(0,c.useEffect)((()=>{const e=()=>{var e;const n=null==(e=a.current)?void 0:e.getBoundingClientRect();if(n){var t,l;const e=(null==(t=s.current)?void 0:t.offsetWidth)||200,o=window.innerWidth,r=n.left+10+160+e<=o;i({top:n.bottom+8,left:Math.max(0,n.right-((null==(l=s.current)?void 0:l.offsetWidth)||0)+(r?170:0))})}};return t&&(e(),document.addEventListener("mousedown",u),window.addEventListener("scroll",e),window.addEventListener("resize",e)),()=>{document.removeEventListener("mousedown",u),window.removeEventListener("scroll",e),window.removeEventListener("resize",e)}}),[t]);const u=e=>{var n;!s.current||s.current.contains(e.target)||null!=(n=a.current)&&n.contains(e.target)||l()};return(0,r.FD)(P,{children:[(0,c.cloneElement)(n,{ref:a}),t&&(0,r.Y)(z,{ref:s,style:{top:`${o.top}px`,left:`${o.left}px`},children:e})]})},$e=(e,n)=>{if(null==e||!e.length||!n)return null;const{colId:t,sort:l}=e[0];return t===n?"asc"===l?(0,r.Y)(Ce.A,{}):"desc"===l?(0,r.Y)(be.A,{}):null:null},Se=({displayName:e,enableSorting:n,setSort:t,context:l,column:o,api:i})=>{var s;const{initialSortState:u,onColumnHeaderClicked:d}=l,g=null==o?void 0:o.getColId(),h=null==o?void 0:o.getColDef(),p=o.getUserProvidedColDef(),m=null==h||null==(s=h.context)?void 0:s.isPercentMetric,[v,f]=(0,c.useState)(!1),[C,b]=(0,c.useState)(!1),x=(0,c.useRef)(null),w=null==o?void 0:o.isFilterActive(),P=null==u?void 0:u[0],z=null==p?void 0:p.isMain,M=!z&&(null==p?void 0:p.timeComparisonKey),N=z?g.replace("Main","").trim():g,Y=()=>{d({column:{colId:N,sort:null}}),t(null,!1)},D=e=>{d({column:{colId:N,sort:e}}),t(e,!1)},I=(null==P?void 0:P.colId)===g?null==P?void 0:P.sort:null,T=!(M||I&&"desc"!==I),L=!(M||I&&"asc"!==I),R=(0,r.FD)(A,{children:[T&&(0,r.FD)("div",{onClick:()=>D("asc"),className:"menu-item",children:[(0,r.Y)(Ce.A,{})," ",(0,a.t)("Sort Ascending")]}),L&&(0,r.FD)("div",{onClick:()=>D("desc"),className:"menu-item",children:[(0,r.Y)(be.A,{})," ",(0,a.t)("Sort Descending")]}),P&&(null==P?void 0:P.colId)===g&&(0,r.FD)("div",{onClick:Y,className:"menu-item",children:[(0,r.Y)("span",{style:{fontSize:16},children:"↻"})," ",(0,a.t)("Clear Sort")]})]});return(0,r.FD)(y,{children:[(0,r.FD)($,{onClick:()=>{if(!n||M)return;const e=(null==P?void 0:P.colId)!==g?"asc":"asc"===(null==P?void 0:P.sort)?"desc":null;e?D(e):Y()},className:"custom-header",children:[(0,r.Y)(S,{children:e}),(0,r.Y)(F,{children:$e(u,g)})]}),(0,r.Y)(ye,{content:(0,r.Y)("div",{ref:x}),isOpen:v,onClose:()=>f(!1),children:(0,r.Y)(k,{className:"header-filter",onClick:async e=>{e.stopPropagation(),f(!v);const n=await i.getColumnFilterInstance(o),t=null==n?void 0:n.eGui;t&&x.current&&(x.current.innerHTML="",x.current.appendChild(t))},isFilterActive:w,children:(0,r.Y)(xe,{})})}),!m&&!M&&(0,r.Y)(ye,{content:R,isOpen:C,onClose:()=>b(!1),children:(0,r.Y)("div",{className:"three-dots-menu",onClick:e=>{e.stopPropagation(),b(!C)},children:(0,r.Y)(we,{})})})]})};var Fe=t(13270),ke=t(95113);const Ae=e=>{switch(e.dataType){case i.s.Numeric:return"number";case i.s.Temporal:return"date";case i.s.Boolean:return"boolean";default:return"text"}};function Pe(e){var n,t,l;let o;const r=!(null==e||!e.originalLabel),i=null==e||null==(n=e.key)?void 0:n.includes("Main"),a=!1!==(null==e||null==(t=e.config)?void 0:t.displayTypeIcon),s=!(null==e||null==(l=e.config)||!l.customColumnName);return o=r&&s?"displayTypeIcon"in e.config&&a&&!i?`${e.label} ${e.config.customColumnName}`:e.config.customColumnName:r&&i?e.originalLabel:r&&!a?"":null==e?void 0:e.label,o||""}const ze=({columns:e,data:n,serverPagination:t,isRawRecords:l,defaultAlignPN:o,showCellBars:s,colorPositiveNegative:u,totals:d,columnColorFormatters:g,allowRearrangeColumns:h,basicColorFormatters:p,isUsingTimeComparison:m,emitCrossFilters:v,alignPositiveNegative:f,slice_id:C})=>{const b=(0,c.useCallback)((c=>{var d,b;const{config:x,isMetric:w,isPercentMetric:y,isNumeric:$,key:S,dataType:F,originalLabel:k}=c,A=void 0===x.alignPositiveNegative?o:x.alignPositiveNegative,P=$&&Array.isArray(g)&&g.length>0,z=m&&Array.isArray(p)&&p.length>0,M=null==S?void 0:S.includes("Main"),N=M?S.replace("Main","").trim():S,Y=F===i.s.String||F===i.s.Temporal,D=!z&&!P&&s&&(null==(d=x.showCellBars)||d)&&(w||l||y)&&function(e,n,t){var l;if("number"==typeof(null==t||null==(l=t[0])?void 0:l[e])){const l=t.map((n=>n[e]));return n?[0,(0,le.A)(l.map(Math.abs))]:(0,oe.A)(l)}return null}(S,A||f,n),I=(e=>{switch(e.dataType){case i.s.Numeric:return"agNumberColumnFilter";case i.s.String:return"agMultiColumnFilter";case i.s.Temporal:return"agDateColumnFilter";default:return!0}})(c);return{field:N,headerName:Pe(c),valueFormatter:e=>((e,n)=>{const{value:t,node:l}=e;return!(0,Fe.A)(t)||""===t||t instanceof ke.A&&null===t.input?-1===(null==l?void 0:l.level)?"":"N/A":(null==n.formatter?void 0:n.formatter(t))||t})(e,c),valueGetter:e=>((e,n)=>{var t,l;if(null!=e&&null!=(t=e.colDef)&&t.isMain){const n=`Main ${e.column.getColId()}`;return e.data[n]}return(0,Fe.A)(null==(l=e.data)?void 0:l[e.column.getColId()])?e.data[e.column.getColId()]:n.isNumeric?void 0:""})(e,c),cellStyle:e=>(e=>{var n;const{value:t,colDef:l,rowIndex:o,hasBasicColorFormatters:r,basicColorFormatters:i,hasColumnColorFormatters:a,columnColorFormatters:s,col:c,node:u}=e;let d;var g;a&&s.filter((e=>{var n,t;return(null!=e&&null!=(n=e.column)&&n.includes("Main")?null==e||null==(t=e.column)?void 0:t.replace("Main","").trim():null==e?void 0:e.column)===l.field})).forEach((e=>{const n=!(!t&&0!==t)&&e.getColorFromValue(t);n&&(d=n)})),r&&null!=c&&c.metricName&&"bottom"!==(null==u?void 0:u.rowPinned)&&(d=null==i||null==(g=i[o])||null==(g=g[c.metricName])?void 0:g.backgroundColor);const h=(null==c||null==(n=c.config)?void 0:n.horizontalAlign)||(null!=c&&c.isNumeric?"right":"left");return{backgroundColor:d||"",textAlign:h}})({...e,hasColumnColorFormatters:P,columnColorFormatters:g,hasBasicColorFormatters:z,basicColorFormatters:p,col:c}),cellClass:e=>(e=>{var n;const{col:t,emitCrossFilters:l}=e,o=null==e||null==(n=e.context)?void 0:n.isActiveFilterValue;let r="";var i;return l&&(null!=t&&t.isMetric||(r+=" dt-is-filter"),null!=o&&o(null==t?void 0:t.key,null==e?void 0:e.value)&&(r+=" dt-is-active-filter"),null!=t&&null!=(i=t.config)&&i.truncateLongCells&&(r+=" dt-truncate-cell")),r})({...e,col:c,emitCrossFilters:v}),minWidth:null!=(b=null==x?void 0:x.columnWidth)?b:100,filter:I,...y&&{filterValueGetter:re},...F===i.s.Temporal&&{filterParams:{comparator:ie}},cellDataType:Ae(c),defaultAggFunc:ae(c),initialAggFunc:ae(c),...!(w||y)&&{allowedAggFuncs:["sum","min","max","count","avg","first","last"]},cellRenderer:e=>Y?(e=>{const{node:n,api:t,colDef:l,columns:o,allowRenderHtml:i,value:s,valueFormatted:c}=e;if("bottom"===(null==n?void 0:n.rowPinned)){const e=t.getAllGridColumns().filter((e=>e.isVisible())),n=!e[0].getAggFunc();if(e.length>1&&n&&o[0].key===(null==l?void 0:l.field))return(0,r.FD)(E,{children:[(0,r.Y)(H,{children:(0,a.t)("Summary")}),(0,r.Y)(ue.m,{overlay:de,children:(0,r.Y)(ce.A,{})})]});if(!s)return null}if(!("string"==typeof s||s instanceof Date))return null!=c?c:s;if("string"==typeof s){if(s.startsWith("http://")||s.startsWith("https://"))return(0,r.Y)("a",{href:s,target:"_blank",rel:"noopener noreferrer",children:s});if(i&&(0,se.fE)(s))return(0,r.Y)("div",{dangerouslySetInnerHTML:{__html:(0,se.pn)(s)}})}return(0,r.Y)("div",{children:null!=c?c:s})})(e):fe(e),cellRendererParams:{allowRenderHtml:!0,columns:e,hasBasicColorFormatters:z,col:c,basicColorFormatters:p,valueRange:D,alignPositiveNegative:A||f,colorPositiveNegative:u},context:{isMetric:w,isPercentMetric:y,isNumeric:$},lockPinned:!h,sortable:!t||!y,...t&&{headerComponent:Se,comparator:()=>0,headerComponentParams:{slice_id:C}},isMain:M,...!M&&k&&{columnGroupShow:"open"},...k&&{timeComparisonKey:k},wrapText:!(null!=x&&x.truncateLongCells),autoHeight:!(null!=x&&x.truncateLongCells)}}),[e,n,o,g,p,s,u,m,l,v,h,t,f]),x=JSON.stringify(e);return(0,c.useMemo)((()=>{const n=new Map;return e.reduce(((e,t)=>{const l=b(t);if(null!=t&&t.originalLabel)if(n.has(t.originalLabel))e[n.get(t.originalLabel)].children.push(l);else{const o={headerName:t.originalLabel,marryChildren:!0,openByDefault:!0,children:[l]};n.set(t.originalLabel,e.length),e.push(o)}else e.push(l);return e}),[])}),[x,b])};var Me=t(96627),Ne=t(62952);const Ye=({key:e,value:n,filters:t,timeGrain:l,isActiveFilterValue:o,timestampFormatter:r})=>{let i={...t||{}};i=t&&o(e,n)?{}:{[e]:[n]},Array.isArray(i[e])&&0===i[e].length&&delete i[e];const a=Object.keys(i),s=Object.values(i),c=[];return a.forEach((e=>{var n;const t=e===Me.Tf,l=(0,Ne.A)(null==(n=i)?void 0:n[e]);if(l.length){const e=l.map((e=>t?r(e):e));c.push(`${e.join(", ")}`)}})),{dataMask:{extraFormData:{filters:0===a.length?[]:a.map((e=>{var n;const t=(0,Ne.A)(null==(n=i)?void 0:n[e]);return t.length?{col:e,op:"IN",val:t.map((e=>e instanceof Date?e.getTime():e)),grain:e===Me.Tf?l:void 0}:{col:e,op:"IS NULL"}}))},filterState:{label:c.join(", "),value:s.length?s:null,filters:i&&Object.keys(i).length?i:null}},isCurrentValueSelected:o(e,n)}},De=(e,n)=>{let t=e;return n&&(t-=16),t-80};function Ie(e){var n;const{height:t,columns:l,data:u,includeSearch:d,allowRearrangeColumns:g,pageSize:h,serverPagination:p,rowCount:m,setDataMask:v,serverPaginationData:f,slice_id:C,percentMetrics:b,hasServerPageLengthChanged:x,serverPageLength:w,emitCrossFilters:y,filters:$,timeGrain:S,isRawRecords:F,alignPositiveNegative:k,showCellBars:A,isUsingTimeComparison:P,colorPositiveNegative:z,totals:M,showTotals:N,columnColorFormatters:Y,basicColorFormatters:D,width:I}=e,[T,L]=(0,c.useState)([]);(0,c.useEffect)((()=>{const e=l.filter((e=>(null==e?void 0:e.dataType)===i.s.String)).map((e=>({value:e.key,label:e.label})));o()(e,T)||L(e||[])}),[l]);const R=[{key:"all",label:(0,a.t)("Display all")},{key:"#",label:"#"},{key:"△",label:"△"},{key:"%",label:"%"}],[U,B]=(0,c.useState)([null==R||null==(n=R[0])?void 0:n.key]),E=(0,c.useMemo)((()=>P?0===U.length||U.includes("all")?null==l?void 0:l.filter((e=>{var n;return!1!==(null==e||null==(n=e.config)?void 0:n.visible)})):l.filter((e=>!e.originalLabel||((null==e?void 0:e.label)||"").includes("Main")||U.includes(e.label))).filter((e=>{var n;return!1!==(null==e||null==(n=e.config)?void 0:n.visible)})):l),[l,U]),H=ze({columns:P?E:l,data:u,serverPagination:p,isRawRecords:F,defaultAlignPN:k,showCellBars:A,colorPositiveNegative:z,totals:M,columnColorFormatters:Y,allowRearrangeColumns:g,basicColorFormatters:D,isUsingTimeComparison:P,emitCrossFilters:y,alignPositiveNegative:k,slice_id:C}),G=De(t,d),V=(0,c.useCallback)((function(e,n){var t;return!!$&&(null==(t=$[e])?void 0:t.includes(n))}),[$]),W=(0,c.useCallback)((e=>(0,s.PT)(S)(e)),[S]),q=(0,c.useCallback)((e=>{var n,t;if(y&&e.column&&!(null!=(n=e.column.getColDef().context)&&n.isMetric||null!=(t=e.column.getColDef().context)&&t.isPercentMetric)){const n={key:e.column.getColId(),value:e.value,filters:$,timeGrain:S,isActiveFilterValue:V,timestampFormatter:W};v(Ye(n).dataMask)}}),[y,v,$,S]),j=(0,c.useCallback)(((e,n)=>{const t={...f,currentPage:e,pageSize:n};(0,J.F)(v,t)}),[v]),_=(0,c.useCallback)((e=>{const n={...f,currentPage:0,pageSize:e};(0,J.F)(v,n)}),[v]),Q=(0,c.useCallback)((e=>{var n;const t={...f||{},searchColumn:(null==f?void 0:f.searchColumn)||(null==(n=T[0])?void 0:n.value),searchText:e,currentPage:0};(0,J.F)(v,t)}),[v,T]),X=(0,c.useCallback)((e=>{if(!p)return;const n={...f,sortBy:e};(0,J.F)(v,n)}),[v,p]);return(0,r.Y)(O,{height:t,children:(0,r.Y)(K,{gridHeight:G,data:u||[],colDefsFromProps:H,includeSearch:!!d,allowRearrangeColumns:!!g,pagination:!!h&&!p,pageSize:h||0,serverPagination:p,rowCount:m,onServerPaginationChange:j,onServerPageSizeChange:_,serverPaginationData:f,searchOptions:T,onSearchColChange:e=>{if(!o()(e,null==f?void 0:f.searchColumn)){const n={...f||{},searchColumn:e,searchText:""};(0,J.F)(v,n)}},onSearchChange:Q,onSortChange:X,id:C,handleCrossFilter:q,percentMetrics:b,serverPageLength:w,hasServerPageLengthChanged:x,isActiveFilterValue:V,renderTimeComparisonDropdown:P?()=>(0,r.Y)(te,{comparisonColumns:R,selectedComparisonColumns:U,onSelectionChange:B}):()=>null,cleanedTotals:M||{},showTotals:N,width:I})})}}}]);