"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[9074],{7987:(e,t,n)=>{n.d(t,{RV:()=>s,be:()=>r,cJ:()=>d,ke:()=>c,kw:()=>u,o6:()=>l,oF:()=>i,sw:()=>a,u_:()=>o});const a="previous calendar week",i="previous calendar month",l="previous calendar quarter",r="previous calendar year",o="Current day",c="Current week",d="Current month",s="Current year",u="Current quarter"},13686:(e,t,n)=>{n.d(t,{t:()=>m});var a=n(77189);const i=String.raw`\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:(?:[+-]\d\d:\d\d)|Z)?`,l=String.raw`(?:TODAY|NOW)`,r=String.raw`[+-]?[1-9][0-9]*`,o=String.raw`YEAR|QUARTER|MONTH|WEEK|DAY|HOUR|MINUTE|SECOND`,c=RegExp(String.raw`^DATEADD\(DATETIME\("(${i}|${l})"\),\s(${r}),\s(${o})\)$`,"i"),d=RegExp(String.raw`^${i}$|^${l}$`,"i"),s=["now","today"],u=new Date;u.setHours(0,0,0,0);const h=new Date;h.setHours(0,0,0,0);const p={sinceDatetime:u.setDate(u.getDate()-7).toString(),sinceMode:"relative",sinceGrain:"day",sinceGrainValue:-7,untilDatetime:h.toString(),untilMode:"specific",untilGrain:"day",untilGrainValue:7,anchorMode:"now",anchorValue:"now"},m=e=>{const t=e.split(a.wv);if(2===t.length){const[e,n]=t;if(d.test(e)&&d.test(n)){const t=s.includes(e)?e:"specific",a=s.includes(n)?n:"specific";return{customRange:{...p,sinceDatetime:e,untilDatetime:n,sinceMode:t,untilMode:a},matchedFlag:!0}}const a=e.match(c);if(a&&d.test(n)&&e.includes(n)){const[e,t,i]=a.slice(1),l=s.includes(n)?n:"specific";return{customRange:{...p,sinceGrain:i,sinceGrainValue:parseInt(t,10),sinceDatetime:e,untilDatetime:e,sinceMode:"relative",untilMode:l},matchedFlag:!0}}const i=n.match(c);if(d.test(e)&&i&&n.includes(e)){const[t,n,a]=[...i.slice(1)],l=s.includes(e)?e:"specific";return{customRange:{...p,untilGrain:a,untilGrainValue:parseInt(n,10),sinceDatetime:t,untilDatetime:t,untilMode:"relative",sinceMode:l},matchedFlag:!0}}if(a&&i){const[e,t,n]=[...a.slice(1)],[l,r,o]=[...i.slice(1)];if(e===l)return{customRange:{...p,sinceGrain:n,sinceGrainValue:parseInt(t,10),sinceDatetime:e,untilGrain:o,untilGrainValue:parseInt(r,10),untilDatetime:l,anchorValue:e,sinceMode:"relative",untilMode:"relative",anchorMode:"now"===e?"now":"specific"},matchedFlag:!0}}}return{customRange:p,matchedFlag:!1}}},22533:(e,t,n)=>{n.d(t,{A:()=>c,v:()=>r});var a=n(2445),i=n(96540),l=n(20900);const r=()=>{var e;return null==(e=document.getElementById("controlSections"))?void 0:e.lastElementChild},o=e=>{var t,n;const a=null==(t=window)?void 0:t.innerHeight,i=null==(n=window)?void 0:n.innerWidth,l=null==e?void 0:e.getBoundingClientRect();return a&&i&&null!=l&&l.top?{yRatio:l.top/a,xRatio:l.left/i}:{yRatio:0,xRatio:0}},c=({getPopupContainer:e,getVisibilityRatio:t=o,open:n,destroyTooltipOnHide:c=!1,placement:d="right",...s})=>{const u=(0,i.useRef)(),[h,p]=(0,i.useState)(void 0===n?s.defaultOpen:n),[m,v]=i.useState(d),g=(0,i.useCallback)((()=>{if(!u.current)return;const{yRatio:e,xRatio:n}=t(u.current),a=n<.35?"right":n>.65?"left":"",i=e<.35?a?"top":"bottom":e>.65?a?"bottom":"top":"",l=(a?a+i.charAt(0).toUpperCase()+i.slice(1):i)||"left";l!==m&&v(l)}),[t]),f=(0,i.useCallback)((e=>{const t=r();t&&t.style.setProperty("overflow-y",e?"hidden":"auto","important")}),[g]),C=(0,i.useCallback)((t=>(u.current=t,(null==e?void 0:e(t))||document.body)),[g,e]),Y=(0,i.useCallback)((e=>{void 0===e&&f(e),p(!!e),null==s.onOpenChange||s.onOpenChange(!!e)}),[s,f]),b=(0,i.useCallback)((e=>{"Escape"===e.key&&(p(!1),null==s.onOpenChange||s.onOpenChange(!1))}),[s]);return(0,i.useEffect)((()=>{void 0!==n&&p(!!n)}),[n]),(0,i.useEffect)((()=>{void 0!==h&&f(h)}),[h,f]),(0,i.useEffect)((()=>(h&&document.addEventListener("keydown",b),()=>{document.removeEventListener("keydown",b)})),[b,h]),(0,i.useEffect)((()=>{h&&g()}),[h,g]),(0,a.Y)(l.A,{...s,open:h,arrow:{pointAtCenter:!0},placement:m,onOpenChange:Y,getPopupContainer:C,destroyTooltipOnHide:c})}},37827:(e,t,n)=>{n.d(t,{A:()=>l,P:()=>i});var a=n(96540);const i={name:"l8l8b8",styles:"white-space:nowrap;overflow:hidden;text-overflow:ellipsis"},l=({isVertical:e,isHorizontal:t}={isVertical:!1,isHorizontal:!0})=>{const[n,i]=(0,a.useState)(!0),l=(0,a.useRef)(null),[r,o]=(0,a.useState)(0),[c,d]=(0,a.useState)(0),[s,u]=(0,a.useState)(0),[h,p]=(0,a.useState)(0);return(0,a.useEffect)((()=>{var e,t,n,a,i,r,c,s;o(null!=(e=null==(t=l.current)?void 0:t.offsetWidth)?e:0),d(null!=(n=null==(a=l.current)?void 0:a.scrollWidth)?n:0),u(null!=(i=null==(r=l.current)?void 0:r.offsetHeight)?i:0),p(null!=(c=null==(s=l.current)?void 0:s.scrollHeight)?c:0)})),(0,a.useEffect)((()=>{i(e&&s<h||t&&r<c)}),[r,c,s,h,e,t]),[l,n]}},39074:(e,t,n)=>{n.d(t,{Ay:()=>a.A});var a=n(45267);n(39942)},39304:(e,t,n)=>{n.d(t,{c:()=>r});var a=n(2445),i=n(17437),l=n(36552);function r(e){return(0,a.Y)(l.A,{css:e=>i.AH`
        margin: ${e.margin}px 0;
      `,...e})}},39942:(e,t,n)=>{n.d(t,{cn:()=>d,oo:()=>Y,nS:()=>s,z6:()=>o,Be:()=>C,OL:()=>c,yI:()=>b,ZC:()=>u,Ex:()=>h,c1:()=>y,ad:()=>D,BJ:()=>r,bd:()=>w,IZ:()=>m,Wm:()=>g,s6:()=>v,OP:()=>f,IS:()=>F,Ab:()=>S,J5:()=>R,IM:()=>O});var a=n(95070),i=n(95579),l=n(7987);const r=[{value:"Common",label:(0,i.t)("Last")},{value:"Calendar",label:(0,i.t)("Previous")},{value:"Current",label:(0,i.t)("Current")},{value:"Custom",label:(0,i.t)("Custom")},{value:"Advanced",label:(0,i.t)("Advanced")},{value:"No filter",label:(0,i.t)("No filter")}],o=[{value:"Last day",label:(0,i.t)("Last day")},{value:"Last week",label:(0,i.t)("Last week")},{value:"Last month",label:(0,i.t)("Last month")},{value:"Last quarter",label:(0,i.t)("Last quarter")},{value:"Last year",label:(0,i.t)("Last year")}],c=new Set(o.map((e=>e.value))),d=[{value:l.sw,label:(0,i.t)("previous calendar week")},{value:l.oF,label:(0,i.t)("previous calendar month")},{value:l.o6,label:(0,i.t)("previous calendar quarter")},{value:l.be,label:(0,i.t)("previous calendar year")}],s=new Set(d.map((e=>e.value))),u=[{value:l.u_,label:(0,i.t)("Current day")},{value:l.ke,label:(0,i.t)("Current week")},{value:l.cJ,label:(0,i.t)("Current month")},{value:l.kw,label:(0,i.t)("Current quarter")},{value:l.RV,label:(0,i.t)("Current year")}],h=new Set(u.map((e=>e.value))),p=[{value:"second",label:e=>(0,i.t)("Seconds %s",e)},{value:"minute",label:e=>(0,i.t)("Minutes %s",e)},{value:"hour",label:e=>(0,i.t)("Hours %s",e)},{value:"day",label:e=>(0,i.t)("Days %s",e)},{value:"week",label:e=>(0,i.t)("Weeks %s",e)},{value:"month",label:e=>(0,i.t)("Months %s",e)},{value:"quarter",label:e=>(0,i.t)("Quarters %s",e)},{value:"year",label:e=>(0,i.t)("Years %s",e)}],m=p.map((e=>({value:e.value,label:e.label((0,i.t)("Before"))}))),v=p.map((e=>({value:e.value,label:e.label((0,i.t)("After"))}))),g=[{value:"specific",label:(0,i.t)("Specific Date/Time")},{value:"relative",label:(0,i.t)("Relative Date/Time")},{value:"now",label:(0,i.t)("Now")},{value:"today",label:(0,i.t)("Midnight")}],f=g.slice(),C=new Set(["Last day","Last week","Last month","Last quarter","Last year"]),Y=new Set([l.sw,l.oF,l.o6,l.be]),b=new Set([l.u_,l.ke,l.cJ,l.kw,l.RV]),y="YYYY-MM-DD[T]HH:mm:ss",w=((0,a.XV)().utc().startOf("day").subtract(7,"days").format(y),(0,a.XV)().utc().startOf("day").format(y));var D;!function(e){e.CommonFrame="common-frame",e.ModalOverlay="modal-overlay",e.PopoverOverlay="time-range-trigger",e.NoFilter="no-filter",e.CancelButton="cancel-button",e.ApplyButton="date-filter-control__apply-button"}(D||(D={}));const A=String.raw`\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:(?:[+-]\d\d:\d\d)|Z)?`,$=String.raw`(?:TODAY|NOW)`,x=(RegExp(String.raw`^${A}$|^${$}$`,"i"),["specific","today","now"]),S=e=>"now"===e?(0,a.XV)().utc().startOf("second"):"today"===e?(0,a.XV)().utc().startOf("day"):(0,a.XV)(e),E=e=>S(e).format(y),F=e=>{const{sinceDatetime:t,sinceMode:n,sinceGrain:a,sinceGrainValue:i,untilDatetime:l,untilMode:r,untilGrain:o,untilGrainValue:c,anchorValue:d}={...e};if(x.includes(n)&&x.includes(r))return`${"specific"===n?E(t):n} : ${"specific"===r?E(l):r}`;if(x.includes(n)&&"relative"===r){const e="specific"===n?E(t):n;return`${e} : DATEADD(DATETIME("${e}"), ${c}, ${o})`}if("relative"===n&&x.includes(r)){const e="specific"===r?E(l):r;return`DATEADD(DATETIME("${e}"), ${-Math.abs(i)}, ${a}) : ${e}`}return`DATEADD(DATETIME("${d}"), ${-Math.abs(i)}, ${a}) : DATEADD(DATETIME("${d}"), ${c}, ${o})`};var T=n(96627),M=n(13686),N=n(61225);const R=e=>c.has(e)?"Common":s.has(e)?"Calendar":h.has(e)?"Current":e===T.WC?"No filter":(0,M.t)(e).matchedFlag?"Custom":"Advanced";function O(){var e;return null!=(e=(0,N.d4)((e=>{var t;return null==e||null==(t=e.common)||null==(t=t.conf)?void 0:t.DEFAULT_TIME_FILTER})))?e:T.WC}},45267:(e,t,n)=>{n.d(t,{A:()=>X});var a=n(2445),i=n(96540),l=n(72234),r=n(17437),o=n(37827),c=n(96627),d=n(77189),s=n(95579),u=n(71781),h=n(87843),p=n(39304),m=n(15509),v=n(97470),g=n(84335),f=n(50317),C=n(38380),Y=n(85183),b=n(15151),y=n(70856),w=n(22533),D=n(39942),A=n(19834);function $(e){let t="Last week";return D.Be.has(e.value)?t=e.value:e.onChange(t),(0,a.FD)(a.FK,{children:[(0,a.Y)("div",{className:"section-title","data-test":D.ad.CommonFrame,children:(0,s.t)("Configure Time Range: Last...")}),(0,a.Y)(A.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!1},size:"large",value:t,onChange:t=>e.onChange(t.target.value),options:D.z6})]})}var x=n(7987);function S({onChange:e,value:t}){return(0,i.useEffect)((()=>{D.oo.has(t)||e(x.sw)}),[e,t]),D.oo.has(t)?(0,a.FD)(a.FK,{children:[(0,a.Y)("div",{className:"section-title",children:(0,s.t)("Configure Time Range: Previous...")}),(0,a.Y)(A.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!1},size:"large",value:t,onChange:t=>e(t.target.value),options:D.cn})]}):null}function E({onChange:e,value:t}){return(0,i.useEffect)((()=>{D.yI.has(t)||e(x.ke)}),[t]),D.yI.has(t)?(0,a.FD)(a.FK,{children:[(0,a.Y)("div",{className:"section-title",children:(0,s.t)("Configure Time Range: Current...")}),(0,a.Y)(A.s.GroupWrapper,{spaceConfig:{direction:"vertical",size:15,align:"start",wrap:!0},size:"large",onChange:t=>{let n=t.target.value;n=n.trim(),""!==n&&e(n)},options:D.ZC})]}):null}var F=n(13686),T=n(52879),M=n(96896),N=n(47152),R=n(16370),O=n(18062),k=n(9707),I=n(2020),V=n(28532);function L(e){const{customRange:t,matchedFlag:n}=(0,F.t)(e.value),i=(0,V.Y)();n||e.onChange((0,D.IS)(t));const{sinceDatetime:l,sinceMode:r,sinceGrain:o,sinceGrainValue:c,untilDatetime:d,untilMode:h,untilGrain:p,untilGrainValue:m,anchorValue:v,anchorMode:g}={...t};function f(n,a){e.onChange((0,D.IS)({...t,[n]:a}))}function C(n,a){"number"==typeof a&&Number.isInteger(a)&&a>0&&e.onChange((0,D.IS)({...t,[n]:a}))}return null===i?(0,a.Y)(T.R,{position:"inline-centered"}):(0,a.Y)(M.Q,{locale:i,children:(0,a.FD)("div",{"data-test":"custom-frame",children:[(0,a.Y)("div",{className:"section-title",children:(0,s.t)("Configure custom time range")}),(0,a.FD)(N.A,{gutter:24,children:[(0,a.FD)(R.A,{span:12,children:[(0,a.FD)("div",{className:"control-label",children:[(0,s.t)("Start (inclusive)")," ",(0,a.Y)(O.I,{tooltip:(0,s.t)("Start date included in time range"),placement:"right"})]}),(0,a.Y)(u.A,{ariaLabel:(0,s.t)("Start (inclusive)"),options:D.Wm,value:r,onChange:e=>f("sinceMode",e)}),"specific"===r&&(0,a.Y)(N.A,{children:(0,a.Y)(k.l,{showTime:!0,defaultValue:(0,D.Ab)(l),onChange:e=>f("sinceDatetime",e.format(D.c1)),allowClear:!1,getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})}),"relative"===r&&(0,a.FD)(N.A,{gutter:8,children:[(0,a.Y)(R.A,{span:11,children:(0,a.Y)(I.A,{placeholder:(0,s.t)("Relative quantity"),value:Math.abs(c),min:1,defaultValue:1,onChange:e=>C("sinceGrainValue",e||1),onStep:e=>C("sinceGrainValue",e||1)})}),(0,a.Y)(R.A,{span:13,children:(0,a.Y)(u.A,{ariaLabel:(0,s.t)("Relative period"),options:D.IZ,value:o,onChange:e=>f("sinceGrain",e)})})]})]}),(0,a.FD)(R.A,{span:12,children:[(0,a.FD)("div",{className:"control-label",children:[(0,s.t)("End (exclusive)")," ",(0,a.Y)(O.I,{tooltip:(0,s.t)("End date excluded from time range"),placement:"right"})]}),(0,a.Y)(u.A,{ariaLabel:(0,s.t)("End (exclusive)"),options:D.OP,value:h,onChange:e=>f("untilMode",e)}),"specific"===h&&(0,a.Y)(N.A,{children:(0,a.Y)(k.l,{showTime:!0,defaultValue:(0,D.Ab)(d),onChange:e=>f("untilDatetime",e.format(D.c1)),allowClear:!1,getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})}),"relative"===h&&(0,a.FD)(N.A,{gutter:8,children:[(0,a.Y)(R.A,{span:11,children:(0,a.Y)(I.A,{placeholder:(0,s.t)("Relative quantity"),value:m,min:1,defaultValue:1,onChange:e=>C("untilGrainValue",e||1),onStep:e=>C("untilGrainValue",e||1)})}),(0,a.Y)(R.A,{span:13,children:(0,a.Y)(u.A,{ariaLabel:(0,s.t)("Relative period"),options:D.s6,value:p,onChange:e=>f("untilGrain",e)})})]})]})]}),"relative"===r&&"relative"===h&&(0,a.FD)("div",{className:"control-anchor-to",children:[(0,a.Y)("div",{className:"control-label",children:(0,s.t)("Anchor to")}),(0,a.FD)(N.A,{align:"middle",children:[(0,a.Y)(R.A,{children:(0,a.Y)(A.s.GroupWrapper,{options:[{value:"now",label:(0,s.t)("Now")},{value:"specific",label:(0,s.t)("Date/Time")}],onChange:function(n){const a=n.target.value;"now"===a?e.onChange((0,D.IS)({...t,anchorValue:"now",anchorMode:a})):e.onChange((0,D.IS)({...t,anchorValue:D.bd,anchorMode:a}))},defaultValue:"now",value:g})}),"now"!==g&&(0,a.Y)(R.A,{children:(0,a.Y)(k.l,{showTime:!0,defaultValue:(0,D.Ab)(v),onChange:e=>f("anchorValue",e.format(D.c1)),allowClear:!1,className:"control-anchor-to-datetime",getPopupContainer:t=>e.isOverflowingFilterBar?t.parentNode:document.body})})]})]})]})})}var G=n(17355);const z=(0,a.FD)(a.FK,{children:[(0,a.FD)("div",{children:[(0,a.Y)("h3",{children:"DATETIME"}),(0,a.Y)("p",{children:(0,s.t)("Return to specific datetime.")}),(0,a.Y)("h4",{children:(0,s.t)("Syntax")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:"datetime([string])"})}),(0,a.Y)("h4",{children:(0,s.t)("Example")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:'datetime("2020-03-01 12:00:00")\ndatetime("now")\ndatetime("last year")'})})]}),(0,a.FD)("div",{children:[(0,a.Y)("h3",{children:"DATEADD"}),(0,a.Y)("p",{children:(0,s.t)("Moves the given set of dates by a specified interval.")}),(0,a.Y)("h4",{children:(0,s.t)("Syntax")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:"dateadd([datetime], [integer], [dateunit])\ndateunit = (year | quarter | month | week | day | hour | minute | second)"})}),(0,a.Y)("h4",{children:(0,s.t)("Example")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:'dateadd(datetime("today"), -13, day)\ndateadd(datetime("2020-03-01"), 2, day)'})})]}),(0,a.FD)("div",{children:[(0,a.Y)("h3",{children:"DATETRUNC"}),(0,a.Y)("p",{children:(0,s.t)("Truncates the specified date to the accuracy specified by the date unit.")}),(0,a.Y)("h4",{children:(0,s.t)("Syntax")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:"datetrunc([datetime], [dateunit])\ndateunit = (year | quarter | month | week)"})}),(0,a.Y)("h4",{children:(0,s.t)("Example")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:'datetrunc(datetime("2020-03-01"), week)\ndatetrunc(datetime("2020-03-01"), month)'})})]}),(0,a.FD)("div",{children:[(0,a.Y)("h3",{children:"LASTDAY"}),(0,a.Y)("p",{children:(0,s.t)("Get the last date by the date unit.")}),(0,a.Y)("h4",{children:(0,s.t)("Syntax")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:"lastday([datetime], [dateunit])\ndateunit = (year | month | week)"})}),(0,a.Y)("h4",{children:(0,s.t)("Example")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:'lastday(datetime("today"), month)'})})]}),(0,a.FD)("div",{children:[(0,a.Y)("h3",{children:"HOLIDAY"}),(0,a.Y)("p",{children:(0,s.t)("Get the specify date for the holiday")}),(0,a.Y)("h4",{children:(0,s.t)("Syntax")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:"holiday([string])\nholiday([holiday string], [datetime])\nholiday([holiday string], [datetime], [country name])"})}),(0,a.Y)("h4",{children:(0,s.t)("Example")}),(0,a.Y)("pre",{children:(0,a.Y)("code",{children:'holiday("new year")\nholiday("christmas", datetime("2019"))\nholiday("christmas", dateadd(datetime("2019"), 1, year))\nholiday("christmas", datetime("2 years ago"))\nholiday("Easter Monday", datetime("2019"), "UK")'})})]})]}),W=e=>{const t=(0,l.DP)();return(0,a.Y)(r.Z2,{children:({css:n})=>(0,a.Y)(v.m,{overlayClassName:n`
            .ant-tooltip-content {
              min-width: ${125*t.sizeUnit}px;
              max-height: 410px;
              overflow-y: scroll;

              .ant-tooltip-inner {
                max-width: ${125*t.sizeUnit}px;
                h3 {
                  font-size: ${t.fontSize}px;
                  font-weight: ${t.fontWeightStrong};
                }
                h4 {
                  font-size: ${t.fontSize}px;
                  font-weight: ${t.fontWeightStrong};
                }
                pre {
                  border: none;
                  text-align: left;
                  word-break: break-word;
                  font-size: ${t.fontSizeSM}px;
                }
              }
            }
          `,...e})})};function P(e){return(0,a.Y)(W,{title:z,...e})}function H(e){return e.includes(d.wv)?e:e.startsWith("Last")?[e,""].join(d.wv):e.startsWith("Next")?["",e].join(d.wv):d.wv}function B(e){const t=H(e.value||""),[n,i]=t.split(d.wv);function l(t,a){"since"===t?e.onChange(`${a}${d.wv}${i}`):e.onChange(`${n}${d.wv}${a}`)}return t!==e.value&&e.onChange(H(e.value||"")),(0,a.FD)(a.FK,{children:[(0,a.FD)("div",{className:"section-title",children:[(0,s.t)("Configure Advanced Time Range "),(0,a.Y)(P,{placement:"rightBottom",children:(0,a.Y)(C.F.InfoCircleOutlined,{})})]}),(0,a.FD)("div",{className:"control-label",children:[(0,s.t)("Start (inclusive)")," ",(0,a.Y)(O.I,{tooltip:(0,s.t)("Start date included in time range"),placement:"right"})]}),(0,a.Y)(G.A,{value:n,onChange:e=>l("since",e.target.value)},"since"),(0,a.FD)("div",{className:"control-label",children:[(0,s.t)("End (exclusive)")," ",(0,a.Y)(O.I,{tooltip:(0,s.t)("End date excluded from time range"),placement:"right"})]}),(0,a.Y)(G.A,{value:i,onChange:e=>l("until",e.target.value)},"until")]})}const U="#45BED6",q=l.I4.div`
  ${({theme:e,isActive:t,isPlaceholder:n})=>r.AH`
    height: ${8*e.sizeUnit}px;

    display: flex;
    align-items: center;
    flex-wrap: nowrap;

    padding: 0 ${3*e.sizeUnit}px;

    background-color: ${e.colors.grayscale.light5};

    border: 1px solid
      ${t?U:e.colors.grayscale.light2};
    border-radius: ${e.borderRadius}px;

    cursor: pointer;

    transition: border-color 0.3s cubic-bezier(0.65, 0.05, 0.36, 1);
    :hover,
    :focus {
      border-color: ${U};
    }

    .date-label-content {
      color: ${n?e.colors.grayscale.light1:e.colorText};
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
      flex-shrink: 1;
      white-space: nowrap;
    }

    span[role='img'] {
      margin-left: auto;
      padding-left: ${e.sizeUnit}px;

      & > span[role='img'] {
        line-height: 0;
      }
    }
  `}
`,_=(0,i.forwardRef)(((e,t)=>(0,a.FD)(q,{...e,tabIndex:0,role:"button",children:[(0,a.Y)("span",{id:`date-label-${e.name}`,className:"date-label-content",ref:t,children:"string"==typeof e.label?(0,s.t)(e.label):e.label}),(0,a.Y)(C.F.CalendarOutlined,{iconSize:"s"})]}))),K=(0,l.I4)(u.A)`
  width: 272px;
`,Z=l.I4.div`
  ${({theme:e})=>r.AH`
    .ant-row {
      margin-top: 8px;
    }

    .ant-picker {
      padding: 4px 17px 4px;
      border-radius: 4px;
    }

    .ant-divider-horizontal {
      margin: 16px 0;
    }

    .control-label {
      font-size: ${e.fontSizeSM}px;
      line-height: 16px;
      margin: 8px 0;
    }

    .section-title {
      font-style: normal;
      font-weight: ${e.fontWeightStrong};
      font-size: 15px;
      line-height: 24px;
      margin-bottom: 8px;
    }

    .control-anchor-to {
      margin-top: 16px;
    }

    .control-anchor-to-datetime {
      width: 217px;
    }

    .footer {
      text-align: right;
    }
  `}
`,J=l.I4.span`
  span {
    margin-right: ${({theme:e})=>2*e.sizeUnit}px;
    vertical-align: middle;
  }
  .text {
    vertical-align: middle;
  }
  .error {
    color: ${({theme:e})=>e.colorError};
  }
`,j=(e,t,n)=>e?(0,a.FD)("div",{children:[t&&(0,a.Y)("strong",{children:t}),n&&(0,a.Y)("div",{css:e=>r.AH`
            margin-top: ${e.sizeUnit}px;
          `,children:n})]}):n||null;function X(e){var t;const{name:n,onChange:r,onOpenPopover:u=b.fZ,onClosePopover:A=b.fZ,overlayStyle:x="Popover",isOverflowingFilterBar:F=!1}=e,T=(0,D.IM)(),M=null!=(t=e.value)?t:T,[N,R]=(0,i.useState)(M),[O,k]=(0,i.useState)(!1),I=(0,i.useMemo)((()=>(0,D.J5)(M)),[M]),[V,G]=(0,i.useState)(I),[z,W]=(0,i.useState)(M),[P,H]=(0,i.useState)(M),[U,q]=(0,i.useState)(!1),[X,Q]=(0,i.useState)(M),[ee,te]=(0,i.useState)(M),ne=(0,l.DP)(),[ae,ie]=(0,o.A)();function le(){H(M),G(I),k(!1),A()}(0,i.useEffect)((()=>{if(M===c.WC)return R(c.WC),te(null),void q(!0);(0,d.x9)(M).then((({value:e,error:t})=>{t?(Q(t||""),q(!1),te(M||null)):("Common"===I||"Calendar"===I||"Current"===I||"No filter"===I?(R(M),te(j(ie,M,e))):(R(e||""),te(j(ie,e,M))),q(!0)),W(M),Q(e||M)}))}),[I,ie,ae,M]),(0,Y.sv)((()=>{if(P===c.WC)return Q(c.WC),W(c.WC),void q(!0);z!==P&&(0,d.x9)(P).then((({value:e,error:t})=>{t?(Q(t||""),q(!1)):(Q(e||""),q(!0)),W(P)}))}),h.Y.SLOW_DEBOUNCE,[P]);const re=()=>{O?le():(H(M),G(I),k(!0),u())},oe=(0,a.FD)(Z,{children:[(0,a.Y)("div",{className:"control-label",children:(0,s.t)("Range type")}),(0,a.Y)(K,{ariaLabel:(0,s.t)("Range type"),options:D.BJ,value:V,onChange:function(e){e===c.WC&&H(c.WC),G(e)}}),"No filter"!==V&&(0,a.Y)(p.c,{}),"Common"===V&&(0,a.Y)($,{value:P,onChange:H}),"Calendar"===V&&(0,a.Y)(S,{value:P,onChange:H}),"Current"===V&&(0,a.Y)(E,{value:P,onChange:H}),"Advanced"===V&&(0,a.Y)(B,{value:P,onChange:H}),"Custom"===V&&(0,a.Y)(L,{value:P,onChange:H,isOverflowingFilterBar:F}),"No filter"===V&&(0,a.Y)("div",{"data-test":D.ad.NoFilter}),(0,a.Y)(p.c,{}),(0,a.FD)("div",{children:[(0,a.Y)("div",{className:"section-title",children:(0,s.t)("Actual time range")}),U&&(0,a.Y)("div",{children:"No filter"===X?(0,s.t)("No filter"):X}),!U&&(0,a.FD)(J,{className:"warning",children:[(0,a.Y)(C.F.ExclamationCircleOutlined,{iconColor:ne.colorError}),(0,a.Y)("span",{className:"text error",children:X})]})]}),(0,a.Y)(p.c,{}),(0,a.FD)("div",{className:"footer",children:[(0,a.Y)(m.$,{buttonStyle:"secondary",cta:!0,onClick:le,"data-test":D.ad.CancelButton,children:(0,s.t)("CANCEL")},"cancel"),(0,a.Y)(m.$,{buttonStyle:"primary",cta:!0,disabled:!U,onClick:function(){r(P),k(!1),A()},"data-test":D.ad.ApplyButton,children:(0,s.t)("APPLY")},"apply")]})]}),ce=(0,a.Y)(w.A,{autoAdjustOverflow:!1,trigger:"click",placement:"right",content:oe,title:(0,a.FD)(J,{children:[(0,a.Y)(C.F.EditOutlined,{}),(0,a.Y)("span",{className:"text",children:(0,s.t)("Edit time range")})]}),defaultOpen:O,open:O,onOpenChange:re,overlayStyle:{width:"600px"},destroyTooltipOnHide:!0,getPopupContainer:e=>F?e.parentNode:document.body,overlayClassName:"time-range-popover",children:(0,a.Y)(v.m,{placement:"top",title:ee,children:(0,a.Y)(_,{name:n,"aria-labelledby":`filter-name-${e.name}`,"aria-describedby":`date-label-${e.name}`,label:N,isActive:O,isPlaceholder:N===c.WC,"data-test":D.ad.PopoverOverlay,ref:ae})})}),de=(0,a.FD)(a.FK,{children:[(0,a.Y)(v.m,{placement:"top",title:ee,children:(0,a.Y)(_,{name:n,"aria-labelledby":`filter-name-${e.name}`,"aria-describedby":`date-label-${e.name}`,onClick:re,label:N,isActive:O,isPlaceholder:N===c.WC,"data-test":D.ad.ModalOverlay,ref:ae})}),(0,a.Y)(g.aF,{title:(0,a.Y)(y.r,{className:"text",isEditMode:!0,title:(0,s.t)("Edit time range")}),name:(0,s.t)("Edit time range"),show:O,onHide:re,width:"600px",hideFooter:!0,zIndex:1030,children:oe})]});return(0,a.FD)(a.FK,{children:[(0,a.Y)(f.A,{...e}),"Modal"===x?de:ce]})}},77189:(e,t,n)=>{n.d(t,{wv:()=>s,x9:()=>m});var a=n(62193),i=n.n(a),l=n(58561),r=n.n(l),o=n(62952),c=n(35742),d=n(51436);const s=" : ",u=(e,t)=>`${e}${s}${t}`,h=(e,t)=>e.replace("T00:00:00","")||(t?"-∞":"∞"),p=(e,t="col")=>{const n=e.split(s);return 1===n.length?e:`${h(n[0],!0)} ≤ ${t} < ${h(n[1])}`},m=async(e,t="col",n)=>{let a,l;if(i()(n))a=r().encode_uri(e),l=`/api/v1/time_range/?q=${a}`;else{const t=(0,o.A)(n).map((t=>({timeRange:e,shift:t})));a=r().encode_uri([{timeRange:e},...t]),l=`/api/v1/time_range/?q=${a}`}try{var m;const e=await c.A.get({endpoint:l});if(i()(n)){var v,g;const n=u((null==e||null==(v=e.json)||null==(v=v.result[0])?void 0:v.since)||"",(null==e||null==(g=e.json)||null==(g=g.result[0])?void 0:g.until)||"");return{value:p(n,t)}}const a=null==e||null==(m=e.json)?void 0:m.result.map((e=>u(e.since,e.until)));return{value:a.slice(1).map((e=>((e,t,n="col")=>{const a=e.split(s),i=t.split(s);return`${n}: ${h(a[0],!0)} to ${h(a[1])} vs\n  ${h(i[0],!0)} to ${h(i[1])}`})(a[0],e,t)))}}catch(e){const t=await(0,d.h4)(e);return{error:t.message||t.error||e.statusText}}}}}]);