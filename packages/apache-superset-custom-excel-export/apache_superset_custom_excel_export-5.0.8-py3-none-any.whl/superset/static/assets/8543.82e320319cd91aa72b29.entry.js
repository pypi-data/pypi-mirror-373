"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[8543],{14118:(e,t,o)=>{o.d(t,{M:()=>$});var n=o(2445),r=o(72234),a=o(95579),i=o(91996),l=o(18062),c=o(97470),d=o(38380),s=o(15509),m=o(17355),p=o(62799),b=o(56268);const g=(0,r.I4)(m.A)`
  margin: ${({theme:e})=>`${e.sizeUnit}px 0 ${2*e.sizeUnit}px`};
`,u=(0,r.I4)(m.A.Password)`
  margin: ${({theme:e})=>`${e.sizeUnit}px 0 ${2*e.sizeUnit}px`};
`,h=(0,r.I4)("div")`
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  margin-bottom: ${({theme:e})=>3*e.sizeUnit}px;
  .ant-form-item {
    margin-bottom: 0;
  }
`,x=(0,r.I4)(p.l)`
  margin-bottom: 0;
`,$=({label:e,validationMethods:t,errorMessage:o,helpText:r,required:m=!1,hasTooltip:p=!1,tooltipText:$,id:f,className:v,visibilityToggle:k,get_url:y,description:_,isValidating:w=!1,...z})=>{const S=!!o;return(0,n.FD)(h,{className:v,children:[(0,n.FD)(i.s,{align:"center",children:[(0,n.Y)(x,{htmlFor:f,required:m,children:e}),p&&(0,n.Y)(l.I,{tooltip:`${$}`})]}),(0,n.FD)(b.e,{validateTrigger:Object.keys(t),validateStatus:w?"validating":S?"error":"success",help:o||r,hasFeedback:!!S,children:[k||"password"===z.name?(0,n.Y)(u,{...z,...t,iconRender:e=>e?(0,n.Y)(c.m,{title:(0,a.t)("Hide password."),children:(0,n.Y)(d.F.EyeInvisibleOutlined,{iconSize:"m"})}):(0,n.Y)(c.m,{title:(0,a.t)("Show password."),children:(0,n.Y)(d.F.EyeOutlined,{iconSize:"m","data-test":"icon-eye"})}),role:"textbox"}):(0,n.Y)(g,{...z,...t}),y&&_?(0,n.FD)(s.$,{type:"link",htmlType:"button",onClick:()=>(window.open(y),!0),children:["Get ",_]}):(0,n.Y)("br",{})]})]})}},28292:(e,t,o)=>{o.d(t,{B:()=>r});var n=o(61225);function r(){return(0,n.d4)((e=>{var t;return null==e||null==(t=e.common)?void 0:t.conf}))}},29221:(e,t,o)=>{o.d(t,{l:()=>a});var n=o(2445),r=o(89467);const a=Object.assign((function(e){return(0,n.Y)(r.A,{...e})}),{useForm:r.A.useForm,Item:r.A.Item,List:r.A.List,ErrorList:r.A.ErrorList,Provider:r.A.Provider})},52219:(e,t,o)=>{o.d(t,{S9:()=>b,YU:()=>s,_p:()=>h,iN:()=>u,nt:()=>p,pw:()=>m,rN:()=>g});var n=o(2445),r=o(96540),a=o(90569),i=o(72234),l=o(17437);const c={"mode/sql":()=>o.e(2514).then(o.t.bind(o,32514,23)),"mode/markdown":()=>Promise.all([o.e(7472),o.e(9620),o.e(9846),o.e(7613)]).then(o.t.bind(o,7613,23)),"mode/css":()=>Promise.all([o.e(9620),o.e(9994)]).then(o.t.bind(o,29994,23)),"mode/json":()=>o.e(9118).then(o.t.bind(o,59118,23)),"mode/yaml":()=>o.e(7215).then(o.t.bind(o,97215,23)),"mode/html":()=>Promise.all([o.e(7472),o.e(9620),o.e(9846),o.e(6861)]).then(o.t.bind(o,56861,23)),"mode/javascript":()=>Promise.all([o.e(7472),o.e(8263)]).then(o.t.bind(o,8263,23)),"theme/textmate":()=>o.e(2694).then(o.t.bind(o,52694,23)),"theme/github":()=>o.e(3139).then(o.t.bind(o,83139,23)),"ext/language_tools":()=>o.e(6464).then(o.t.bind(o,6464,23)),"ext/searchbox":()=>o.e(8949).then(o.t.bind(o,88949,23))};function d(e,{defaultMode:t,defaultTheme:d,defaultTabSize:s=2,fontFamily:m="Menlo, Consolas, Courier New, Ubuntu Mono, source-code-pro, Lucida Console, monospace",placeholder:p}={}){return(0,a.x)((async()=>{var a,p;const b=Promise.all([o.e(952),o.e(470)]).then(o.bind(o,70470)),g=o.e(952).then(o.t.bind(o,80952,23)),u=o.e(9234).then(o.t.bind(o,19234,23)),h=o.e(4987).then(o.t.bind(o,34987,23)),[{default:x},{config:$},{default:f},{require:v}]=await Promise.all([b,g,u,h]);$.setModuleUrl("ace/mode/css_worker",f),await Promise.all(e.map((e=>c[e]())));const k=t||(null==(a=e.find((e=>e.startsWith("mode/"))))?void 0:a.replace("mode/","")),y=d||(null==(p=e.find((e=>e.startsWith("theme/"))))?void 0:p.replace("theme/",""));return(0,r.forwardRef)((function({keywords:e,mode:t=k,theme:o=y,tabSize:a=s,defaultValue:c="",...d},p){const b=(0,i.DP)(),g=v("ace/ext/language_tools"),u=(0,r.useCallback)((e=>{const o={getCompletions:(o,n,r,a,i)=>{Number.isNaN(parseInt(a,10))&&n.getMode().$id===`ace/mode/${t}`&&i(null,e)}};g.setCompleters([o])}),[g,t]);return(0,r.useEffect)((()=>{e&&u(e)}),[e,u]),(0,n.FD)(n.FK,{children:[(0,n.Y)(l.mL,{styles:l.AH`
                .ace_editor {
                  border: 1px solid ${b.colorBorder} !important;
                  background-color: ${b.colorBgContainer} !important;
                }

                /* Basic editor styles with dark mode support */
                .ace_editor.ace-github,
                .ace_editor.ace-tm {
                  background-color: ${b.colorBgContainer} !important;
                  color: ${b.colorText} !important;
                }

                /* Adjust gutter colors */
                .ace_editor .ace_gutter {
                  background-color: ${b.colorBgElevated} !important;
                  color: ${b.colorTextSecondary} !important;
                }
                .ace_editor.ace_editor .ace_gutter .ace_gutter-active-line {
                  background-color: ${b.colorBorderSecondary};
                }
                /* Adjust selection color */
                .ace_editor .ace_selection {
                  background-color: ${b.colorPrimaryBgHover} !important;
                }

                /* Improve active line highlighting */
                .ace_editor .ace_active-line {
                  background-color: ${b.colorPrimaryBg} !important;
                }

                /* Fix indent guides and print margin (80 chars line) */
                .ace_editor .ace_indent-guide,
                .ace_editor .ace_print-margin {
                  background-color: ${b.colorSplit} !important;
                  opacity: 0.5;
                }

                /* Adjust cursor color */
                .ace_editor .ace_cursor {
                  color: ${b.colorPrimaryText} !important;
                }

                /* Syntax highlighting using semantic color tokens */
                .ace_editor .ace_keyword {
                  color: ${b.colorPrimaryText} !important;
                }

                .ace_editor .ace_string {
                  color: ${b.colorSuccessText} !important;
                }

                .ace_editor .ace_constant {
                  color: ${b.colorWarningActive} !important;
                }

                .ace_editor .ace_function {
                  color: ${b.colorInfoText} !important;
                }

                .ace_editor .ace_comment {
                  color: ${b.colorTextTertiary} !important;
                }

                .ace_editor .ace_variable {
                  color: ${b.colorTextSecondary} !important;
                }

                /* Adjust tooltip styles */
                .ace_tooltip {
                  margin-left: ${b.margin}px;
                  padding: 0px;
                  background-color: ${b.colorBgElevated} !important;
                  color: ${b.colorText} !important;
                  border: 1px solid ${b.colorBorderSecondary};
                  box-shadow: ${b.boxShadow};
                  border-radius: ${b.borderRadius}px;
                }

                & .tooltip-detail {
                  background-color: ${b.colorBgContainer};
                  white-space: pre-wrap;
                  word-break: break-all;
                  min-width: ${5*b.sizeXXL}px;
                  max-width: ${10*b.sizeXXL}px;

                  & .tooltip-detail-head {
                    background-color: ${b.colorBgElevated};
                    color: ${b.colorText};
                    display: flex;
                    column-gap: ${b.padding}px;
                    align-items: baseline;
                    justify-content: space-between;
                  }

                  & .tooltip-detail-title {
                    display: flex;
                    column-gap: ${b.padding}px;
                  }

                  & .tooltip-detail-body {
                    word-break: break-word;
                    color: ${b.colorTextSecondary};
                  }

                  & .tooltip-detail-head,
                  & .tooltip-detail-body {
                    padding: ${b.padding}px ${b.paddingLG}px;
                  }

                  & .tooltip-detail-footer {
                    border-top: 1px ${b.colorSplit} solid;
                    padding: 0 ${b.paddingLG}px;
                    color: ${b.colorTextTertiary};
                    font-size: ${b.fontSizeSM}px;
                  }

                  & .tooltip-detail-meta {
                    & > .ant-tag {
                      margin-right: 0px;
                    }
                  }
                }

                /* Adjust the searchbox to match theme */
                .ace_search {
                  background-color: ${b.colorBgContainer} !important;
                  color: ${b.colorText} !important;
                  border: 1px solid ${b.colorBorder} !important;
                }

                .ace_search_field {
                  background-color: ${b.colorBgContainer} !important;
                  color: ${b.colorText} !important;
                  border: 1px solid ${b.colorBorder} !important;
                }

                .ace_button {
                  background-color: ${b.colorBgElevated} !important;
                  color: ${b.colorText} !important;
                  border: 1px solid ${b.colorBorder} !important;
                }

                .ace_button:hover {
                  background-color: ${b.colorPrimaryBg} !important;
                }
              `},"ace-tooltip-global"),(0,n.Y)(x,{ref:p,mode:t,theme:o,tabSize:a,defaultValue:c,setOptions:{fontFamily:m},...d})]})}))}),p)}const s=d(["mode/sql","theme/github","ext/language_tools","ext/searchbox"]),m=d(["mode/sql","theme/github","ext/language_tools","ext/searchbox"],{placeholder:()=>(0,n.FD)("div",{style:{height:"100%"},children:[(0,n.Y)("div",{style:{width:41,height:"100%",background:"#e8e8e8"}}),(0,n.Y)("div",{className:"ace_content"})]})}),p=d(["mode/markdown","theme/textmate"]),b=d(["mode/markdown","mode/sql","mode/json","mode/html","mode/javascript","theme/textmate"]),g=d(["mode/css","theme/github"]),u=d(["mode/json","theme/github"]),h=d(["mode/json","mode/yaml","theme/github"])},56268:(e,t,o)=>{o.d(t,{e:()=>r});var n=o(89467);const r=(0,o(72234).I4)(n.A.Item)`
  ${({theme:e})=>`\n    &.ant-form-item > .ant-row > .ant-form-item-label {\n      padding-bottom: ${e.paddingXXS}px;\n    }\n    .ant-form-item-label {\n      & > label {\n        font-size: ${e.fontSizeSM}px;\n        &.ant-form-item-required:not(.ant-form-item-required-mark-optional) {\n          &::before {\n            display: none;\n          }\n          &::after {\n            display: inline-block;\n            visibility: visible;\n            color: ${e.colorError};\n            font-size: ${e.fontSizeSM}px;\n            content: '*';\n          }\n        }\n      }\n    }\n    .ant-form-item-extra {\n      margin-top: ${e.sizeUnit}px;\n      font-size: ${e.fontSizeSM}px;\n    }\n  `}
`},63393:(e,t,o)=>{o.d(t,{Ay:()=>h,fn:()=>b,pX:()=>u});var n=o(2445),r=o(72234),a=o(17437),i=o(10277),l=o(38380);const c=({animated:e=!1,allowOverflow:t=!0,...o})=>{const l=(0,r.DP)();return(0,n.Y)(i.A,{animated:e,...o,tabBarStyle:{paddingLeft:4*l.sizeUnit},css:e=>a.AH`
        overflow: ${t?"visible":"hidden"};

        .ant-tabs-content-holder {
          overflow: ${t?"visible":"auto"};
        }
        .ant-tabs-tab {
          flex: 1 1 auto;

          .short-link-trigger.btn {
            padding: 0 ${e.sizeUnit}px;
            & > .fa.fa-link {
              top: 0;
            }
          }
        }
        .ant-tabs-tab-btn {
          display: flex;
          flex: 1 1 auto;
          align-items: center;
          justify-content: center;
          font-size: ${e.fontSizeSM}px;
          text-align: center;
          user-select: none;
          .required {
            margin-left: ${e.sizeUnit/2}px;
            color: ${e.colorError};
          }
          &:focus-visible {
            box-shadow: none;
          }
        }
      `})},d=(0,r.I4)(i.A.TabPane)``,s=Object.assign(c,{TabPane:d}),m=(0,r.I4)(c)`
  ${({theme:e})=>`\n    .ant-tabs-content-holder {\n      background: ${e.colors.grayscale.light5};\n    }\n\n    & > .ant-tabs-nav {\n      margin-bottom: 0;\n    }\n\n    .ant-tabs-tab-remove {\n      padding-top: 0;\n      padding-bottom: 0;\n      height: ${6*e.sizeUnit}px;\n    }\n  `}
`,p=(0,r.I4)(l.F.CloseOutlined)`
  color: ${({theme:e})=>e.colors.grayscale.base};
`,b=Object.assign(m,{TabPane:d});b.defaultProps={type:"editable-card",animated:{inkBar:!0,tabPane:!1}},b.TabPane.defaultProps={closeIcon:(0,n.Y)(p,{iconSize:"s",role:"button",tabIndex:0})};const g=(0,r.I4)(b)`
  &.ant-tabs-card > .ant-tabs-nav .ant-tabs-tab {
    margin: 0 ${({theme:e})=>4*e.sizeUnit}px;
    padding: ${({theme:e})=>`${3*e.sizeUnit}px ${e.sizeUnit}px`};
    background: transparent;
    border: none;
  }

  &.ant-tabs-card > .ant-tabs-nav .ant-tabs-ink-bar {
    visibility: visible;
  }

  .ant-tabs-tab-btn {
    font-size: ${({theme:e})=>e.fontSize}px;
  }

  .ant-tabs-tab-remove {
    margin-left: 0;
    padding-right: 0;
  }

  .ant-tabs-nav-add {
    min-width: unset !important;
    background: transparent !important;
    border: none !important;
  }
`,u=Object.assign(g,{TabPane:d}),h=s},69097:(e,t,o)=>{o.d(t,{s:()=>c});var n=o(2445),r=o(72234),a=o(17437),i=o(64658),l=o(38380);const c=({title:e,subtitle:t,validateCheckStatus:o,testId:c})=>{const d=(0,r.DP)();return(0,n.FD)("div",{"data-test":c,children:[(0,n.FD)(i.o.Title,{css:a.AH`
          && {
            margin-top: 0;
            margin-bottom: ${d.sizeUnit/2}px;
            font-size: ${d.fontSizeLG}px;
          }
        `,children:[e," ",void 0!==o&&(o?(0,n.Y)(l.F.CheckCircleOutlined,{iconColor:d.colorSuccess,"aria-label":"check-circle"}):(0,n.Y)("span",{css:a.AH`
                color: ${d.colorErrorText};
                font-size: ${d.fontSizeLG}px;
              `,children:"*"}))]}),(0,n.Y)(i.o.Paragraph,{css:a.AH`
          margin: 0;
          font-size: ${d.fontSizeSM}px;
          color: ${d.colorTextDescription};
        `,children:t})]})}}}]);