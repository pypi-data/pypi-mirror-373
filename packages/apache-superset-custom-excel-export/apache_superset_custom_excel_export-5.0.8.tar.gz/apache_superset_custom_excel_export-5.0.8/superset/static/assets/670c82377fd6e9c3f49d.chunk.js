"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[3973],{8791:(e,t,a)=>{a.d(t,{Ay:()=>_,Kt:()=>C,cs:()=>v});var n=a(2445),i=a(96540),o=a(72234),r=a(95579),l=a(51436),s=a(88461),d=a(62799),c=a(71781),h=a(44344),m=a(38380),u=a(99340),p=a(25509),g=a(5261),b=a(71478);const f=o.I4.div`
  ${({theme:e})=>`\n    .refresh {\n      display: flex;\n      align-items: center;\n      width: 30px;\n      margin-left: ${e.sizeUnit}px;\n      margin-top: ${5*e.sizeUnit}px;\n    }\n\n    .section {\n      display: flex;\n      flex-direction: row;\n      align-items: center;\n    }\n\n    .divider {\n      border-bottom: 1px solid ${e.colorSplit};\n      margin: 15px 0;\n    }\n\n    .table-length {\n      color: ${e.colors.grayscale.light1};\n    }\n\n    .select {\n      flex: 1;\n      max-width: calc(100% - ${e.sizeUnit+30}px)\n    }\n  `}
`,y=o.I4.span`
  align-items: center;
  display: flex;
  white-space: nowrap;

  svg,
  small {
    margin-right: ${({theme:e})=>e.sizeUnit}px;
  }
`,v=({table:e})=>{const{value:t,type:a,extra:i}=e;return(0,n.FD)(y,{title:t,children:["view"===a?(0,n.Y)(m.F.EyeOutlined,{iconSize:"m"}):(0,n.Y)(m.F.InsertRowAboveOutlined,{iconSize:"m"}),(null==i?void 0:i.certification)&&(0,n.Y)(s.T,{certifiedBy:i.certification.certified_by,details:i.certification.details,size:"l"}),(null==i?void 0:i.warning_markdown)&&(0,n.Y)(p.A,{warningMarkdown:i.warning_markdown,size:"l",marginRight:4}),t]})},x=({database:e,emptyState:t,formMode:a=!1,getDbList:o,handleError:s,isDatabaseSelectEnabled:m=!0,onDbChange:p,onCatalogChange:y,onSchemaChange:x,readOnly:C=!1,onEmptyResults:_,catalog:S,schema:A,sqlLabMode:w=!0,tableSelectMode:Y="single",tableValue:$,onTableSelectChange:T,customTableOptionLabelRenderer:E})=>{const{addSuccessToast:k}=(0,g.Yf)(),[D,z]=(0,i.useState)(S),[I,F]=(0,i.useState)(A),[L,M]=(0,i.useState)(void 0),{currentData:O,isFetching:q,refetch:P}=(0,b.ty)({dbId:null==e?void 0:e.id,catalog:D,schema:I,onSuccess:(e,t)=>{t&&k((0,r.t)("List updated"))},onError:e=>{(0,l.h4)(e).then((e=>{s((0,l.hi)((0,r.t)("There was an error loading the tables"),e))}))}}),U=(0,i.useMemo)((()=>O?O.options.map((e=>({value:e.value,label:E?E(e):(0,n.Y)(v,{table:e}),text:e.value}))):[]),[O,E]);(0,i.useEffect)((()=>{void 0===e&&(z(void 0),F(void 0),M(void 0))}),[e,Y]),(0,i.useEffect)((()=>{M("single"===Y?U.find((e=>e.value===$)):(null==U?void 0:U.filter((e=>e&&(null==$?void 0:$.includes(e.value)))))||[])}),[U,$,Y]);const R=(0,i.useMemo)((()=>(e,t)=>{const a=e.trim().toLowerCase(),{value:n}=t;return n.toLowerCase().includes(a)}),[]);return(0,n.FD)(f,{children:[(0,n.Y)(h.RA,{db:e,emptyState:t,formMode:a,getDbList:o,handleError:s,onDbChange:C?void 0:e=>{p&&p(e),z(void 0),F(void 0),M("single"===Y?void 0:[])},onEmptyResults:_,onCatalogChange:C?void 0:e=>{z(e),y&&y(e),F(void 0),M("single"===Y?void 0:[])},catalog:D,onSchemaChange:C?void 0:e=>{F(e),x&&x(e),M("single"===Y?void 0:[])},schema:I,sqlLabMode:w,isDatabaseSelectEnabled:m&&!C,readOnly:C}),w&&!a&&(0,n.Y)("div",{className:"divider"}),function(){const e=I&&!a&&C||!I,t=w?(0,n.Y)(d.l,{children:(0,r.t)("See table schema")}):(0,n.Y)(d.l,{children:(0,r.t)("Table")});return i=(0,n.Y)(c.A,{ariaLabel:(0,r.t)("Select table or type to search tables"),disabled:e,filterOption:R,header:t,labelInValue:!0,loading:q,name:"select-table",onChange:e=>{return t=e,void(I?null==T||T(Array.isArray(t)?t.map((e=>null==e?void 0:e.value)):null==t?void 0:t.value,D,I):M(t));var t},options:U,placeholder:(0,r.t)("Select table or type to search tables"),showSearch:!0,mode:Y,value:L,allowClear:"multiple"===Y,allowSelectAll:!1}),o=!C&&(0,n.Y)(u.A,{onClick:()=>P(),tooltipContent:(0,r.t)("Force refresh table list")}),(0,n.FD)("div",{className:"section",children:[(0,n.Y)("span",{className:"select",children:i}),(0,n.Y)("span",{className:"refresh",children:o})]});var i,o}()]})},C=e=>(0,n.Y)(x,{tableSelectMode:"multiple",...e}),_=x},19855:(e,t,a)=>{a.d(t,{A:()=>f});var n=a(96540),i=a(5556),o=a.n(i),r=a(52219),l=a(97470),s=a(17355),d=a(53784),c=a(15509),h=a(95579),m=a(98837),u=a(50317),p=a(2445);const g={name:o().string,onChange:o().func,initialValue:o().string,height:o().number,minLines:o().number,maxLines:o().number,offerEditInModal:o().bool,language:o().oneOf([null,"json","html","sql","markdown","javascript"]),aboveEditorSection:o().node,readOnly:o().bool,resize:o().oneOf([null,"block","both","horizontal","inline","none","vertical"]),textAreaStyles:o().object,tooltipOptions:o().object,hotkeys:o().array};class b extends n.Component{onControlChange(e){const{value:t}=e.target;this.props.onChange(t)}onAreaEditorChange(e){this.props.onChange(e)}renderEditor(e=!1){const t=e?40:this.props.minLines||12;if(this.props.language){const a={border:`1px solid ${this.props.theme.colorBorder}`,minHeight:`${t}em`,width:"auto",...this.props.textAreaStyles};this.props.resize&&(a.resize=this.props.resize),this.props.readOnly&&(a.backgroundColor="#f2f2f2");const n=e=>{this.props.hotkeys.forEach((t=>{e.commands.addCommand({name:t.name,bindKey:{win:t.key,mac:t.key},exec:t.func})}))},i=(0,p.Y)("div",{children:(0,p.Y)(r.S9,{mode:this.props.language,style:a,minLines:t,maxLines:e?1e3:this.props.maxLines,editorProps:{$blockScrolling:!0},onLoad:n,defaultValue:this.props.initialValue,readOnly:this.props.readOnly,...this.props,onChange:this.onAreaEditorChange.bind(this)},this.props.name)});return this.props.tooltipOptions?(0,p.Y)(l.m,{...this.props.tooltipOptions,children:i}):i}const a=(0,p.Y)("div",{children:(0,p.Y)(s.A.TextArea,{placeholder:(0,h.t)("textarea"),onChange:this.onControlChange.bind(this),defaultValue:this.props.initialValue,disabled:this.props.readOnly,style:{height:this.props.height},"aria-required":this.props["aria-required"]})});return this.props.tooltipOptions?(0,p.Y)(l.m,{...this.props.tooltipOptions,children:a}):a}renderModalBody(){return(0,p.FD)(p.FK,{children:[(0,p.Y)("div",{children:this.props.aboveEditorSection}),this.renderEditor(!0)]})}render(){const e=(0,p.Y)(u.A,{...this.props});return(0,p.FD)("div",{children:[e,this.renderEditor(),this.props.offerEditInModal&&(0,p.Y)(d.g,{modalTitle:e,triggerNode:(0,p.FD)(c.$,{buttonSize:"small",style:{marginTop:this.props.theme.sizeUnit},children:[(0,h.t)("Edit")," ",(0,p.Y)("strong",{children:this.props.language})," ",(0,h.t)("in modal")]}),modalBody:this.renderModalBody(!0),responsive:!0})]})}}b.propTypes=g,b.defaultProps={onChange:()=>{},initialValue:"",height:250,minLines:3,maxLines:10,offerEditInModal:!0,readOnly:!1,resize:null,textAreaStyles:{},tooltipOptions:{},hotkeys:[]};const f=(0,m.b)(b)},29221:(e,t,a)=>{a.d(t,{l:()=>o});var n=a(2445),i=a(89467);const o=Object.assign((function(e){return(0,n.Y)(i.A,{...e})}),{useForm:i.A.useForm,Item:i.A.Item,List:i.A.List,ErrorList:i.A.ErrorList,Provider:i.A.Provider})},30983:(e,t,a)=>{a.d(t,{Z:()=>o});var n=a(2445),i=a(677);const o=Object.assign((({padded:e,...t})=>(0,n.Y)(i.A,{...t,css:t=>({".ant-card-body":{padding:e?4*t.sizeUnit:t.sizeUnit}})})),{Meta:i.A.Meta})},36552:(e,t,a)=>{a.d(t,{A:()=>b});var n=a(96540),i=a(46942),o=a.n(i),r=a(62279),l=a(829),s=a(77132),d=a(25905),c=a(37358),h=a(14277);const m=e=>{const{componentCls:t}=e;return{[t]:{"&-horizontal":{[`&${t}`]:{"&-sm":{marginBlock:e.marginXS},"&-md":{marginBlock:e.margin}}}}}},u=e=>{const{componentCls:t,sizePaddingEdgeHorizontal:a,colorSplit:n,lineWidth:i,textPaddingInline:o,orientationMargin:r,verticalMarginInline:l}=e;return{[t]:Object.assign(Object.assign({},(0,d.dF)(e)),{borderBlockStart:`${(0,s.zA)(i)} solid ${n}`,"&-vertical":{position:"relative",top:"-0.06em",display:"inline-block",height:"0.9em",marginInline:l,marginBlock:0,verticalAlign:"middle",borderTop:0,borderInlineStart:`${(0,s.zA)(i)} solid ${n}`},"&-horizontal":{display:"flex",clear:"both",width:"100%",minWidth:"100%",margin:`${(0,s.zA)(e.marginLG)} 0`},[`&-horizontal${t}-with-text`]:{display:"flex",alignItems:"center",margin:`${(0,s.zA)(e.dividerHorizontalWithTextGutterMargin)} 0`,color:e.colorTextHeading,fontWeight:500,fontSize:e.fontSizeLG,whiteSpace:"nowrap",textAlign:"center",borderBlockStart:`0 ${n}`,"&::before, &::after":{position:"relative",width:"50%",borderBlockStart:`${(0,s.zA)(i)} solid transparent`,borderBlockStartColor:"inherit",borderBlockEnd:0,transform:"translateY(50%)",content:"''"}},[`&-horizontal${t}-with-text-start`]:{"&::before":{width:`calc(${r} * 100%)`},"&::after":{width:`calc(100% - ${r} * 100%)`}},[`&-horizontal${t}-with-text-end`]:{"&::before":{width:`calc(100% - ${r} * 100%)`},"&::after":{width:`calc(${r} * 100%)`}},[`${t}-inner-text`]:{display:"inline-block",paddingBlock:0,paddingInline:o},"&-dashed":{background:"none",borderColor:n,borderStyle:"dashed",borderWidth:`${(0,s.zA)(i)} 0 0`},[`&-horizontal${t}-with-text${t}-dashed`]:{"&::before, &::after":{borderStyle:"dashed none none"}},[`&-vertical${t}-dashed`]:{borderInlineStartWidth:i,borderInlineEnd:0,borderBlockStart:0,borderBlockEnd:0},"&-dotted":{background:"none",borderColor:n,borderStyle:"dotted",borderWidth:`${(0,s.zA)(i)} 0 0`},[`&-horizontal${t}-with-text${t}-dotted`]:{"&::before, &::after":{borderStyle:"dotted none none"}},[`&-vertical${t}-dotted`]:{borderInlineStartWidth:i,borderInlineEnd:0,borderBlockStart:0,borderBlockEnd:0},[`&-plain${t}-with-text`]:{color:e.colorText,fontWeight:"normal",fontSize:e.fontSize},[`&-horizontal${t}-with-text-start${t}-no-default-orientation-margin-start`]:{"&::before":{width:0},"&::after":{width:"100%"},[`${t}-inner-text`]:{paddingInlineStart:a}},[`&-horizontal${t}-with-text-end${t}-no-default-orientation-margin-end`]:{"&::before":{width:"100%"},"&::after":{width:0},[`${t}-inner-text`]:{paddingInlineEnd:a}}})}},p=(0,c.OF)("Divider",(e=>{const t=(0,h.oX)(e,{dividerHorizontalWithTextGutterMargin:e.margin,sizePaddingEdgeHorizontal:0});return[u(t),m(t)]}),(e=>({textPaddingInline:"1em",orientationMargin:.05,verticalMarginInline:e.marginXS})),{unitless:{orientationMargin:!0}});const g={small:"sm",middle:"md"},b=e=>{const{getPrefixCls:t,direction:a,className:i,style:s}=(0,r.TP)("divider"),{prefixCls:d,type:c="horizontal",orientation:h="center",orientationMargin:m,className:u,rootClassName:b,children:f,dashed:y,variant:v="solid",plain:x,style:C,size:_}=e,S=function(e,t){var a={};for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&t.indexOf(n)<0&&(a[n]=e[n]);if(null!=e&&"function"==typeof Object.getOwnPropertySymbols){var i=0;for(n=Object.getOwnPropertySymbols(e);i<n.length;i++)t.indexOf(n[i])<0&&Object.prototype.propertyIsEnumerable.call(e,n[i])&&(a[n[i]]=e[n[i]])}return a}(e,["prefixCls","type","orientation","orientationMargin","className","rootClassName","children","dashed","variant","plain","style","size"]),A=t("divider",d),[w,Y,$]=p(A),T=(0,l.A)(_),E=g[T],k=!!f,D=n.useMemo((()=>"left"===h?"rtl"===a?"end":"start":"right"===h?"rtl"===a?"start":"end":h),[a,h]),z="start"===D&&null!=m,I="end"===D&&null!=m,F=o()(A,i,Y,$,`${A}-${c}`,{[`${A}-with-text`]:k,[`${A}-with-text-${D}`]:k,[`${A}-dashed`]:!!y,[`${A}-${v}`]:"solid"!==v,[`${A}-plain`]:!!x,[`${A}-rtl`]:"rtl"===a,[`${A}-no-default-orientation-margin-start`]:z,[`${A}-no-default-orientation-margin-end`]:I,[`${A}-${E}`]:!!E},u,b),L=n.useMemo((()=>"number"==typeof m?m:/^\d+$/.test(m)?Number(m):m),[m]),M={marginInlineStart:z?L:void 0,marginInlineEnd:I?L:void 0};return w(n.createElement("div",Object.assign({className:F,style:Object.assign(Object.assign({},s),C)},S,{role:"separator"}),f&&"vertical"!==c&&n.createElement("span",{className:`${A}-inner-text`,style:M},f)))}},39304:(e,t,a)=>{a.d(t,{c:()=>r});var n=a(2445),i=a(17437),o=a(36552);function r(e){return(0,n.Y)(o.A,{css:e=>i.AH`
        margin: ${e.margin}px 0;
      `,...e})}},50317:(e,t,a)=>{a.d(t,{A:()=>m});var n=a(2445),i=a(17437),o=a(72234),r=a(95579),l=a(97470),s=a(18062),d=a(62799),c=a(38380);const h=i.AH`
  &.anticon {
    font-size: unset;
    .anticon {
      line-height: unset;
      vertical-align: unset;
    }
  }
`,m=({name:e,label:t,description:a,validationErrors:m=[],renderTrigger:u=!1,rightNode:p,leftNode:g,onClick:b,hovered:f=!1,tooltipOnClick:y=()=>{},warning:v,danger:x})=>{const C=(0,o.DP)();return t?(0,n.FD)("div",{className:"ControlHeader","data-test":`${e}-header`,children:[(0,n.Y)("div",{className:"pull-left",children:(0,n.FD)(d.l,{css:e=>i.AH`
            margin-bottom: ${.5*e.sizeUnit}px;
            position: relative;
            font-size: ${e.fontSizeSM}px;
          `,htmlFor:e,children:[g&&(0,n.FD)("span",{children:[g," "]}),(0,n.Y)("span",{role:"button",tabIndex:0,onClick:b,style:{cursor:b?"pointer":""},children:t})," ",v&&(0,n.FD)("span",{children:[(0,n.Y)(l.m,{id:"error-tooltip",placement:"top",title:v,children:(0,n.Y)(c.F.WarningOutlined,{iconColor:C.colorWarning,css:i.AH`
                    vertical-align: baseline;
                  `,iconSize:"s"})})," "]}),x&&(0,n.FD)("span",{children:[(0,n.Y)(l.m,{id:"error-tooltip",placement:"top",title:x,children:(0,n.Y)(c.F.CloseCircleOutlined,{iconColor:C.colorErrorText,iconSize:"s"})})," "]}),(null==m?void 0:m.length)>0&&(0,n.FD)("span",{"data-test":"error-tooltip",children:[(0,n.Y)(l.m,{id:"error-tooltip",placement:"top",title:null==m?void 0:m.join(" "),children:(0,n.Y)(c.F.CloseCircleOutlined,{iconColor:C.colorErrorText})})," "]}),f?(0,n.FD)("span",{css:()=>i.AH`
          position: absolute;
          top: 60%;
          right: 0;
          padding-left: ${C.sizeUnit}px;
          transform: translate(100%, -50%);
          white-space: nowrap;
        `,children:[a&&(0,n.FD)("span",{children:[(0,n.Y)(l.m,{id:"description-tooltip",title:a,placement:"top",children:(0,n.Y)(c.F.InfoCircleOutlined,{css:h,onClick:y})})," "]}),u&&(0,n.FD)("span",{children:[(0,n.Y)(s.I,{label:(0,r.t)("bolt"),tooltip:(0,r.t)("Changing this control takes effect instantly"),placement:"top",type:"notice"})," "]})]}):null]})}),p&&(0,n.Y)("div",{className:"pull-right",children:p}),(0,n.Y)("div",{className:"clearfix"})]}):null}},52219:(e,t,a)=>{a.d(t,{S9:()=>u,YU:()=>c,_p:()=>b,iN:()=>g,nt:()=>m,pw:()=>h,rN:()=>p});var n=a(2445),i=a(96540),o=a(90569),r=a(72234),l=a(17437);const s={"mode/sql":()=>a.e(2514).then(a.t.bind(a,32514,23)),"mode/markdown":()=>Promise.all([a.e(7472),a.e(9620),a.e(9846),a.e(7613)]).then(a.t.bind(a,7613,23)),"mode/css":()=>Promise.all([a.e(9620),a.e(9994)]).then(a.t.bind(a,29994,23)),"mode/json":()=>a.e(9118).then(a.t.bind(a,59118,23)),"mode/yaml":()=>a.e(7215).then(a.t.bind(a,97215,23)),"mode/html":()=>Promise.all([a.e(7472),a.e(9620),a.e(9846),a.e(6861)]).then(a.t.bind(a,56861,23)),"mode/javascript":()=>Promise.all([a.e(7472),a.e(8263)]).then(a.t.bind(a,8263,23)),"theme/textmate":()=>a.e(2694).then(a.t.bind(a,52694,23)),"theme/github":()=>a.e(3139).then(a.t.bind(a,83139,23)),"ext/language_tools":()=>a.e(6464).then(a.t.bind(a,6464,23)),"ext/searchbox":()=>a.e(8949).then(a.t.bind(a,88949,23))};function d(e,{defaultMode:t,defaultTheme:d,defaultTabSize:c=2,fontFamily:h="Menlo, Consolas, Courier New, Ubuntu Mono, source-code-pro, Lucida Console, monospace",placeholder:m}={}){return(0,o.x)((async()=>{var o,m;const u=Promise.all([a.e(952),a.e(470)]).then(a.bind(a,70470)),p=a.e(952).then(a.t.bind(a,80952,23)),g=a.e(9234).then(a.t.bind(a,19234,23)),b=a.e(4987).then(a.t.bind(a,34987,23)),[{default:f},{config:y},{default:v},{require:x}]=await Promise.all([u,p,g,b]);y.setModuleUrl("ace/mode/css_worker",v),await Promise.all(e.map((e=>s[e]())));const C=t||(null==(o=e.find((e=>e.startsWith("mode/"))))?void 0:o.replace("mode/","")),_=d||(null==(m=e.find((e=>e.startsWith("theme/"))))?void 0:m.replace("theme/",""));return(0,i.forwardRef)((function({keywords:e,mode:t=C,theme:a=_,tabSize:o=c,defaultValue:s="",...d},m){const u=(0,r.DP)(),p=x("ace/ext/language_tools"),g=(0,i.useCallback)((e=>{const a={getCompletions:(a,n,i,o,r)=>{Number.isNaN(parseInt(o,10))&&n.getMode().$id===`ace/mode/${t}`&&r(null,e)}};p.setCompleters([a])}),[p,t]);return(0,i.useEffect)((()=>{e&&g(e)}),[e,g]),(0,n.FD)(n.FK,{children:[(0,n.Y)(l.mL,{styles:l.AH`
                .ace_editor {
                  border: 1px solid ${u.colorBorder} !important;
                  background-color: ${u.colorBgContainer} !important;
                }

                /* Basic editor styles with dark mode support */
                .ace_editor.ace-github,
                .ace_editor.ace-tm {
                  background-color: ${u.colorBgContainer} !important;
                  color: ${u.colorText} !important;
                }

                /* Adjust gutter colors */
                .ace_editor .ace_gutter {
                  background-color: ${u.colorBgElevated} !important;
                  color: ${u.colorTextSecondary} !important;
                }
                .ace_editor.ace_editor .ace_gutter .ace_gutter-active-line {
                  background-color: ${u.colorBorderSecondary};
                }
                /* Adjust selection color */
                .ace_editor .ace_selection {
                  background-color: ${u.colorPrimaryBgHover} !important;
                }

                /* Improve active line highlighting */
                .ace_editor .ace_active-line {
                  background-color: ${u.colorPrimaryBg} !important;
                }

                /* Fix indent guides and print margin (80 chars line) */
                .ace_editor .ace_indent-guide,
                .ace_editor .ace_print-margin {
                  background-color: ${u.colorSplit} !important;
                  opacity: 0.5;
                }

                /* Adjust cursor color */
                .ace_editor .ace_cursor {
                  color: ${u.colorPrimaryText} !important;
                }

                /* Syntax highlighting using semantic color tokens */
                .ace_editor .ace_keyword {
                  color: ${u.colorPrimaryText} !important;
                }

                .ace_editor .ace_string {
                  color: ${u.colorSuccessText} !important;
                }

                .ace_editor .ace_constant {
                  color: ${u.colorWarningActive} !important;
                }

                .ace_editor .ace_function {
                  color: ${u.colorInfoText} !important;
                }

                .ace_editor .ace_comment {
                  color: ${u.colorTextTertiary} !important;
                }

                .ace_editor .ace_variable {
                  color: ${u.colorTextSecondary} !important;
                }

                /* Adjust tooltip styles */
                .ace_tooltip {
                  margin-left: ${u.margin}px;
                  padding: 0px;
                  background-color: ${u.colorBgElevated} !important;
                  color: ${u.colorText} !important;
                  border: 1px solid ${u.colorBorderSecondary};
                  box-shadow: ${u.boxShadow};
                  border-radius: ${u.borderRadius}px;
                }

                & .tooltip-detail {
                  background-color: ${u.colorBgContainer};
                  white-space: pre-wrap;
                  word-break: break-all;
                  min-width: ${5*u.sizeXXL}px;
                  max-width: ${10*u.sizeXXL}px;

                  & .tooltip-detail-head {
                    background-color: ${u.colorBgElevated};
                    color: ${u.colorText};
                    display: flex;
                    column-gap: ${u.padding}px;
                    align-items: baseline;
                    justify-content: space-between;
                  }

                  & .tooltip-detail-title {
                    display: flex;
                    column-gap: ${u.padding}px;
                  }

                  & .tooltip-detail-body {
                    word-break: break-word;
                    color: ${u.colorTextSecondary};
                  }

                  & .tooltip-detail-head,
                  & .tooltip-detail-body {
                    padding: ${u.padding}px ${u.paddingLG}px;
                  }

                  & .tooltip-detail-footer {
                    border-top: 1px ${u.colorSplit} solid;
                    padding: 0 ${u.paddingLG}px;
                    color: ${u.colorTextTertiary};
                    font-size: ${u.fontSizeSM}px;
                  }

                  & .tooltip-detail-meta {
                    & > .ant-tag {
                      margin-right: 0px;
                    }
                  }
                }

                /* Adjust the searchbox to match theme */
                .ace_search {
                  background-color: ${u.colorBgContainer} !important;
                  color: ${u.colorText} !important;
                  border: 1px solid ${u.colorBorder} !important;
                }

                .ace_search_field {
                  background-color: ${u.colorBgContainer} !important;
                  color: ${u.colorText} !important;
                  border: 1px solid ${u.colorBorder} !important;
                }

                .ace_button {
                  background-color: ${u.colorBgElevated} !important;
                  color: ${u.colorText} !important;
                  border: 1px solid ${u.colorBorder} !important;
                }

                .ace_button:hover {
                  background-color: ${u.colorPrimaryBg} !important;
                }
              `},"ace-tooltip-global"),(0,n.Y)(f,{ref:m,mode:t,theme:a,tabSize:o,defaultValue:s,setOptions:{fontFamily:h},...d})]})}))}),m)}const c=d(["mode/sql","theme/github","ext/language_tools","ext/searchbox"]),h=d(["mode/sql","theme/github","ext/language_tools","ext/searchbox"],{placeholder:()=>(0,n.FD)("div",{style:{height:"100%"},children:[(0,n.Y)("div",{style:{width:41,height:"100%",background:"#e8e8e8"}}),(0,n.Y)("div",{className:"ace_content"})]})}),m=d(["mode/markdown","theme/textmate"]),u=d(["mode/markdown","mode/sql","mode/json","mode/html","mode/javascript","theme/textmate"]),p=d(["mode/css","theme/github"]),g=d(["mode/json","theme/github"]),b=d(["mode/json","mode/yaml","theme/github"])},53674:(e,t,a)=>{a.d(t,{A:()=>i});var n=a(95579);function i(e){return!(!e||!Number.isNaN(Number(e)))&&(0,n.t)("is expected to be a number")}},56268:(e,t,a)=>{a.d(t,{e:()=>i});var n=a(89467);const i=(0,a(72234).I4)(n.A.Item)`
  ${({theme:e})=>`\n    &.ant-form-item > .ant-row > .ant-form-item-label {\n      padding-bottom: ${e.paddingXXS}px;\n    }\n    .ant-form-item-label {\n      & > label {\n        font-size: ${e.fontSizeSM}px;\n        &.ant-form-item-required:not(.ant-form-item-required-mark-optional) {\n          &::before {\n            display: none;\n          }\n          &::after {\n            display: inline-block;\n            visibility: visible;\n            color: ${e.colorError};\n            font-size: ${e.fontSizeSM}px;\n            content: '*';\n          }\n        }\n      }\n    }\n    .ant-form-item-extra {\n      margin-top: ${e.sizeUnit}px;\n      font-size: ${e.fontSizeSM}px;\n    }\n  `}
`},57940:(e,t,a)=>{a.d(t,{A:()=>s,Q:()=>r});var n=a(4923),i=a(53682),o=a(32142);const r=e=>{var t;return null==(t=new Intl.NumberFormat("en-US",{style:"currency",currency:e.symbol}).formatToParts(1).find((e=>"currency"===e.type)))?void 0:t.value};class l extends n.A{constructor(e){super((e=>this.format(e))),this.d3Format=void 0,this.locale=void 0,this.currency=void 0,this.d3Format=e.d3Format||i.A.SMART_NUMBER,this.currency=e.currency,this.locale=e.locale||"en-US"}hasValidCurrency(){var e;return Boolean(null==(e=this.currency)?void 0:e.symbol)}getNormalizedD3Format(){return this.d3Format.replace(/\$|%/g,"")}format(e){const t=(0,o.gV)(this.getNormalizedD3Format())(e);return this.hasValidCurrency()?"prefix"===this.currency.symbolPosition?`${r(this.currency)} ${t}`:`${t} ${r(this.currency)}`:t}}const s=l},63393:(e,t,a)=>{a.d(t,{Ay:()=>b,fn:()=>u,pX:()=>g});var n=a(2445),i=a(72234),o=a(17437),r=a(10277),l=a(38380);const s=({animated:e=!1,allowOverflow:t=!0,...a})=>{const l=(0,i.DP)();return(0,n.Y)(r.A,{animated:e,...a,tabBarStyle:{paddingLeft:4*l.sizeUnit},css:e=>o.AH`
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
      `})},d=(0,i.I4)(r.A.TabPane)``,c=Object.assign(s,{TabPane:d}),h=(0,i.I4)(s)`
  ${({theme:e})=>`\n    .ant-tabs-content-holder {\n      background: ${e.colors.grayscale.light5};\n    }\n\n    & > .ant-tabs-nav {\n      margin-bottom: 0;\n    }\n\n    .ant-tabs-tab-remove {\n      padding-top: 0;\n      padding-bottom: 0;\n      height: ${6*e.sizeUnit}px;\n    }\n  `}
`,m=(0,i.I4)(l.F.CloseOutlined)`
  color: ${({theme:e})=>e.colors.grayscale.base};
`,u=Object.assign(h,{TabPane:d});u.defaultProps={type:"editable-card",animated:{inkBar:!0,tabPane:!1}},u.TabPane.defaultProps={closeIcon:(0,n.Y)(m,{iconSize:"s",role:"button",tabIndex:0})};const p=(0,i.I4)(u)`
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
`,g=Object.assign(p,{TabPane:d}),b=c},65482:(e,t,a)=>{function n(e,t){return e===t||!e&&!t||!!(e&&t&&e.length===t.length&&e.every(((e,a)=>e===t[a])))}a.d(t,{A:()=>n})},77686:(e,t,a)=>{a.d(t,{E:()=>r});var n=a(2445),i=a(72234),o=a(52120);const r=(0,i.I4)((e=>(0,n.Y)(o.A,{...e})))`
  ${({theme:e,color:t,count:a})=>`\n    & > sup,\n    & > sup.ant-badge-count {\n      ${void 0!==a?`background: ${t||e.colorPrimary};`:""}\n    }\n  `}
`},82281:(e,t,a)=>{a.d(t,{z:()=>g});var n=a(2445),i=a(72234),o=a(17437),r=a(95579),l=a(96540),s=a(46942),d=a.n(s),c=a(97470),h=a(88461),m=a(17355);const u=(0,i.I4)(h.T)`
  vertical-align: middle;
`,p=i.I4.span`
  &.editable-title {
    display: inline-block;
    width: 100%;

    input,
    textarea {
      outline: none;
      background: transparent;
      box-shadow: none;
      cursor: initial;
      font-feature-settings:
        'liga' 0,
        'calt' 0;
      font-variant-ligatures: none;
      font-weight: bold;
    }

    input[type='text'],
    textarea {
      border: 1px solid ${({theme:e})=>e.colorSplit};
      color: ${({theme:e})=>e.colorTextTertiary};
      border-radius: ${({theme:e})=>e.sizeUnit}px;
      font-size: ${({theme:e})=>e.fontSizeLG}px;
      padding: ${({theme:e})=>e.sizeUnit/2}px;
      min-height: 100px;
      width: 95%;
    }

    &.datasource-sql-expression {
      min-width: 315px;
      width: 100%;
    }
  }
`;function g({canEdit:e=!1,editing:t=!1,extraClasses:a,noPermitTooltip:i,onSaveTitle:s,showTooltip:h=!0,style:g,title:b="",defaultTitle:f="",placeholder:y="",certifiedBy:v,certificationDetails:x,renderLink:C,maxWidth:_,autoSize:S=!0,...A}){const[w,Y]=(0,l.useState)(t),[$,T]=(0,l.useState)(b),[E,k]=(0,l.useState)(b),[D,z]=(0,l.useState)(0),I=(0,l.useRef)(null);function F(){const t=$.trim();e&&(Y(!1),t.length?(E!==t&&k(t),b!==t&&s(t)):T(E))}(0,l.useEffect)((()=>{var e;const{font:t}=window.getComputedStyle((null==(e=I.current)||null==(e=e.resizableTextArea)?void 0:e.textArea)||document.body),a=function(e,t="14px Arial"){const a=document.createElement("canvas").getContext("2d");return a?(a.font=t,a.measureText(e).width):0}($||"",t),n="number"==typeof _?_:1/0;z(Math.min(a+20,n))}),[$]),(0,l.useEffect)((()=>{b!==$&&(k($),T(b))}),[b]),(0,l.useEffect)((()=>{if(w&&I.current){var e;const t=null==(e=I.current.resizableTextArea)?void 0:e.textArea;if(t){t.focus();const{length:e}=t.value;t.setSelectionRange(e,e),t.scrollTop=t.scrollHeight}}}),[w]);let L=$;w||$||(L=f||b);let M=(0,n.Y)(m.A.TextArea,{size:"small","data-test":"textarea-editable-title-input",ref:I,value:L,className:b?void 0:"text-muted",onChange:function(t){e&&T(t.target.value)},onBlur:F,onClick:function(){var t;if(!e||w)return;const a=null==(t=I.current)||null==(t=t.resizableTextArea)?void 0:t.textArea;if(a){a.focus();const{length:e}=a.value;a.setSelectionRange(e,e)}Y(!0)},onKeyDown:function(e){["Backspace","Delete"," ","ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(e.key)&&e.stopPropagation(),"Enter"===e.key&&(e.preventDefault(),F())},onPressEnter:function(e){e.preventDefault(),F()},placeholder:y,variant:w?"outlined":"borderless",autoSize:!!S&&{minRows:1,maxRows:3},css:e=>o.AH`
        && {
          width: ${D}px;
          min-width: ${10*e.sizeUnit}px;
          transition: auto;
        }
      `});return h&&!w&&(M=(0,n.Y)(c.m,{id:"title-tooltip",placement:"topLeft",title:e?(0,r.t)("Click to edit"):i||(0,r.t)("You don't have the rights to alter this title."),children:M})),e||(M=C?C(L||""):(0,n.Y)("span",{"data-test":"span-title",children:L})),(0,n.FD)(p,{"data-test":"editable-title",className:d()("editable-title",a,e&&"editable-title--editable",w&&"editable-title--editing"),style:g,editing:w,canEdit:e,...A,children:[v&&(0,n.FD)(n.FK,{children:[(0,n.Y)(u,{certifiedBy:v,details:x,size:"xl"})," "]}),M]})}},88461:(e,t,a)=>{a.d(t,{T:()=>s});var n=a(2445),i=a(72234),o=a(95579),r=a(38380),l=a(97470);function s({certifiedBy:e,details:t,size:a="l"}){const s=(0,i.DP)();return(0,n.Y)(l.m,{id:"certified-details-tooltip",title:(0,n.FD)(n.FK,{children:[e&&(0,n.Y)("div",{children:(0,n.Y)("strong",{children:(0,o.t)("Certified by %s",e)})}),(0,n.Y)("div",{children:t})]}),children:(0,n.Y)(r.F.Certified,{iconColor:s.colorPrimary,iconSize:a})})}},95405:(e,t,a)=>{a.r(t),a.d(t,{default:()=>Ue});var n=a(17437),i=a(58561),o=a.n(i),r=a(96540),l=a(5556),s=a.n(l),d=a(61225),c=a(19834),h=a(72391),m=a(72234),u=a(95579),p=a(27366),g=a(35742),b=a(62952),f=a(57940),y=a(51436),v=a(98837),x=a(63393),C=a(25509),_=a(8791),S=a(37648),A=a(4783),w=a(19855),Y=a(9379),$=a(5261),T=a(3173),E=a(77686),k=a(71781),D=a(64658),z=a(88461),I=a(82281),F=a(82537),L=a(30983),M=a(25729),O=a(62799),q=a(52879),P=a(38380),U=a(39304),R=a(16370),N=a(15509),B=a(15757),K=a(47152),j=a(44344);const H=(0,a(93505).A)({method:"POST",endpoint:"/api/v1/sqllab/execute"});function Q(e){return{type:"SET_QUERY_IS_LOADING",payload:e}}var W=a(6411),G=a.n(W),V=a(69732),X=a(2445),J=a(43561),Z=a(18062),ee=a(16537),te=a(29221);function ae(e,t,a){return r.Children.map(e,(e=>{let n=e;return e&&e.type&&e.type.name===t.name&&(n=(0,r.cloneElement)(e,a(e))),n&&n.props&&n.props.children&&(n=(0,r.cloneElement)(n,{children:ae(n.props.children,t,a)})),n}))}var ne=a(97470),ie=a(56268);const oe=n.AH`
  .ant-form-item-control-input-content {
    display: flex;
    flex-direction: row;
  }
`;function re({fieldKey:e,value:t,label:a,description:i=null,control:o,additionalControl:l,onChange:s=()=>{},compact:d=!1,inline:c,errorMessage:h}){const u=(0,r.useCallback)((t=>{s(e,t)}),[s,e]),p=(0,r.cloneElement)(o,{value:t,onChange:u}),g=(0,m.DP)(),b=!d&&i?i:void 0,f=d&&i?(0,X.Y)(ne.m,{css:n.AH`
          color: ${g.colorTextTertiary};
        `,id:"field-descr",placement:"right",title:i,children:(0,X.Y)(P.F.InfoCircleOutlined,{iconSize:"s",css:n.AH`
            margin-left: ${g.sizeUnit}px;
          `,iconColor:g.colorTextTertiary})}):void 0;return(0,X.FD)("div",{css:l&&n.AH`
          position: relative;
        `,children:[l,(0,X.Y)(ie.e,{label:(0,X.FD)(O.l,{children:[a||e,f]}),css:c&&oe,extra:b,children:p}),h&&(0,X.Y)("div",{css:e=>({color:e.colorText,[c?"marginLeft":"marginTop"]:e.sizeUnit}),children:h})]})}function le({children:e,onChange:t,item:a,title:n=null,compact:i=!1}){const o=(0,r.useCallback)(((e,n)=>{t({...a,[e]:n})}),[t,a]);return(0,X.FD)(te.l,{className:"CRUD",layout:"vertical",children:[n&&(0,X.FD)(D.o.Title,{level:5,children:[n," ",(0,X.Y)(U.c,{})]}),ae(e,re,(e=>({onChange:o,value:a[e.props.fieldKey],compact:i})))]})}const se=m.I4.div`
  text-align: right;
  ${({theme:e})=>`margin-bottom: ${2*e.sizeUnit}px`}
`,de=m.I4.span`
  ${({theme:e})=>`\n    margin-top: ${3*e.sizeUnit}px;\n    margin-left: ${3*e.sizeUnit}px;\n    button>span>:first-of-type {\n      margin-right: 0;\n    }\n  `}
`;function ce(e){const t=e.map((e=>({...e,id:e.id||(0,J.Ak)()}))),a={};return t.forEach((e=>{a[e.id]=e})),{collection:a,collectionArray:t}}class he extends r.PureComponent{constructor(e){super(e);const{collection:t,collectionArray:a}=ce(e.collection);this.state={expandedColumns:{},collection:t,collectionArray:a,sortColumn:"",sort:0},this.onAddItem=this.onAddItem.bind(this),this.renderExpandableSection=this.renderExpandableSection.bind(this),this.getLabel=this.getLabel.bind(this),this.onFieldsetChange=this.onFieldsetChange.bind(this),this.changeCollection=this.changeCollection.bind(this),this.handleTableChange=this.handleTableChange.bind(this),this.buildTableColumns=this.buildTableColumns.bind(this),this.toggleExpand=this.toggleExpand.bind(this)}UNSAFE_componentWillReceiveProps(e){if(e.collection!==this.props.collection){const{collection:t,collectionArray:a}=ce(e.collection);this.setState((e=>({collection:t,collectionArray:a,expandedColumns:e.expandedColumns})))}}onCellChange(e,t,a){this.setState((n=>{const i={...n.collection,[e]:{...n.collection[e],[t]:a}},o=n.collectionArray.map((t=>t.id===e?i[e]:t));return this.props.onChange&&this.props.onChange(o),{collection:i,collectionArray:o}}))}onAddItem(){if(this.props.itemGenerator){let e=this.props.itemGenerator();const t=!0===e.expanded;e.id||(e={...e,id:(0,J.Ak)()}),delete e.expanded,this.setState((a=>{const n={...a.collection,[e.id]:e},i=t?{...a.expandedColumns,[e.id]:!0}:a.expandedColumns;return{collection:n,collectionArray:[e,...a.collectionArray],expandedColumns:i}}),(()=>{this.props.onChange&&this.props.onChange(this.state.collectionArray)}))}}onFieldsetChange(e){this.changeCollection({...this.state.collection,[e.id]:e})}getLabel(e){const{columnLabels:t}=this.props;let a=null!=t&&t[e]?t[e]:e;return a.startsWith("__")&&(a=""),a}getTooltip(e){const{columnLabelTooltips:t}=this.props;return null==t?void 0:t[e]}changeCollection(e){const t=function(e){return Object.keys(e).map((t=>e[t]))}(e);this.setState({collection:e,collectionArray:t}),this.props.onChange&&this.props.onChange(t)}deleteItem(e){const t={...this.state.collection};delete t[e],this.changeCollection(t)}toggleExpand(e){this.setState((t=>({expandedColumns:{...t.expandedColumns,[e]:!t.expandedColumns[e]}})))}handleTableChange(e,t,a){const n=Array.isArray(a)?a[0]:a;let i="",o=0;null!=n&&n.columnKey&&null!=n&&n.order&&(i=n.columnKey,o="ascend"===n.order?1:2);const{sortColumns:r}=this.props,l=i;if(null!=r&&r.includes(l)||0===o){let e=[...this.props.collection];if(0!==o){const t=(e,t)=>{if("string"==typeof e&&"string"==typeof t)return(e||"").localeCompare(t||"");if("number"==typeof e&&"number"==typeof t)return e-t;if("boolean"==typeof e&&"boolean"==typeof t)return e===t?0:e?1:-1;const a=String(null!=e?e:""),n=String(null!=t?t:"");return a.localeCompare(n)};e.sort(((e,a)=>t(e[l],a[l]))),2===o&&e.reverse()}else{const{collectionArray:t}=ce(this.props.collection);e=t}this.setState({collectionArray:e,sortColumn:i,sort:o})}}renderExpandableSection(e){return ae(this.props.expandFieldset,le,(()=>({item:e,onChange:this.onFieldsetChange})))}renderCell(e,t){var a;const n=null==(a=this.props.itemRenderers)?void 0:a[t],i=e[t],o=this.onCellChange.bind(this,e.id,t);return n?n(i,o,this.getLabel(t),e):i}buildTableColumns(){const{tableColumns:e,allowDeletes:t,sortColumns:a=[]}=this.props,i=e.map((e=>{const t=this.getLabel(e),n=this.getTooltip(e),i=a.includes(e),o=this.state.sortColumn===e?1===this.state.sort?"ascend":2===this.state.sort?"descend":null:null;return{key:e,dataIndex:e,minWidth:100,title:(0,X.FD)(X.FK,{children:[t,n&&(0,X.FD)(X.FK,{children:[" ",(0,X.Y)(Z.I,{label:(0,u.t)("description"),tooltip:n,placement:"top"})]})]}),render:(t,a)=>this.renderCell(a,e),onCell:a=>{var n;const i=null==(n=this.props.itemCellProps)?void 0:n[e],o=a[e];return i?i(o,t,a):{}},sorter:i,sortOrder:o}}));return t&&i.push({key:"__actions",dataIndex:"__actions",sorter:!1,title:(0,X.Y)(X.FK,{}),onCell:()=>({}),sortOrder:null,minWidth:50,render:(e,t)=>(0,X.Y)("span",{"data-test":"crud-delete-option",className:"text-primary",css:e=>n.AH`
              display: flex;
              justify-content: center;
              color: ${e.colorTextTertiary};
            `,children:(0,X.Y)(P.F.DeleteOutlined,{"aria-label":"Delete item",className:"pointer","data-test":"crud-delete-icon",role:"button",tabIndex:0,onClick:()=>this.deleteItem(t.id),iconSize:"l",iconColor:"inherit"})})}),i}render(){const{stickyHeader:e,emptyMessage:t=(0,u.t)("No items"),expandFieldset:a}=this.props,i=this.buildTableColumns(),o=Object.keys(this.state.expandedColumns).filter((e=>this.state.expandedColumns[e])),r=a?{expandedRowRender:e=>this.renderExpandableSection(e),rowExpandable:()=>!0,expandedRowKeys:o,onExpand:(e,t)=>{this.toggleExpand(t.id)}}:void 0;return(0,X.FD)(X.FK,{children:[(0,X.Y)(se,{children:this.props.allowAddItem&&(0,X.Y)(de,{children:(0,X.FD)(N.$,{buttonSize:"small",buttonStyle:"secondary",onClick:this.onAddItem,"data-test":"add-item-button",children:[(0,X.Y)(P.F.PlusOutlined,{iconSize:"m","data-test":"crud-add-table-item"}),(0,u.t)("Add item")]})})}),(0,X.Y)(ee.Ay,{"data-test":"crud-table",columns:i,data:this.state.collectionArray,rowKey:e=>String(e.id),sticky:e,pagination:!1,onChange:this.handleTableChange,locale:{emptyText:t},css:e&&n.AH`
              height: 350px;
              overflow: auto;
            `,expandable:r,size:ee.QS.Middle,tableLayout:"auto"})]})}}var me;const ue=(0,h.a)(),pe=m.I4.div`
  .change-warning {
    margin: 16px 10px 0;
    color: ${({theme:e})=>e.colorWarning};
  }

  .change-warning .bold {
    font-weight: ${({theme:e})=>e.fontWeightStrong};
  }

  .form-group.has-feedback > .help-block {
    margin-top: 8px;
  }

  .form-group.form-group-md {
    margin-bottom: 8px;
  }
`,ge=m.I4.div`
  align-items: center;
  display: flex;

  svg {
    margin-right: ${({theme:e})=>e.sizeUnit}px;
  }
`,be=(0,m.I4)(x.Ay)`
  overflow: visible;
  .ant-tabs-content-holder {
    overflow: visible;
  }
`,fe=(0,m.I4)(E.E)`
  .ant-badge-count {
    line-height: ${({theme:e})=>4*e.sizeUnit}px;
    height: ${({theme:e})=>4*e.sizeUnit}px;
    margin-left: ${({theme:e})=>e.sizeUnit}px;
  }
`,ye=m.I4.div`
  font-size: ${({theme:e})=>e.fontSizeSM}px;
  display: flex;
  align-items: center;
  a {
    padding: 0 10px;
  }
`,ve=m.I4.div`
  text-align: right;
  ${({theme:e})=>`margin-bottom: ${2*e.sizeUnit}px`}
`,xe=m.I4.div`
  display: flex;
  align-items: center;
  span {
    margin-right: ${({theme:e})=>e.sizeUnit}px;
  }
`,Ce=m.I4.div`
  .table > tbody > tr > td {
    vertical-align: middle;
  }

  .ant-tag {
    margin-top: ${({theme:e})=>e.sizeUnit}px;
  }
`,_e=m.I4.span`
  ${({theme:e})=>`\n    margin-top: ${3*e.sizeUnit}px;\n    margin-left: ${3*e.sizeUnit}px;\n    button>span>:first-of-type {\n      margin-right: 0;\n    }\n  `}
`,Se=(e,t)=>(0,X.Y)(S.A,{value:e,onChange:t}),Ae=[{value:"STRING",label:(0,u.t)("STRING")},{value:"NUMERIC",label:(0,u.t)("NUMERIC")},{value:"DATETIME",label:(0,u.t)("DATETIME")},{value:"BOOLEAN",label:(0,u.t)("BOOLEAN")}],we="SOURCE",Ye=[{key:"physical",label:(0,u.t)("Physical (table or view)")},{key:"virtual",label:(0,u.t)("Virtual (SQL)")}],$e={};Ye.forEach((e=>{$e[e.key]=e}));var Te={name:"s5xdrg",styles:"display:flex;align-items:center"};function Ee({title:e,collection:t}){return(0,X.FD)("div",{css:Te,"data-test":`collection-tab-${e}`,children:[e," ",(0,X.Y)(fe,{count:t?t.length:0,showZero:!0})]})}function ke({columns:e,datasource:t,onColumnsChange:a,onDatasourceChange:n,editableColumnName:i,showExpression:o,allowAddItem:r,allowEditDataType:l,itemGenerator:s,columnLabelTooltips:d}){return(0,X.Y)(he,{tableColumns:(0,p.G7)(p.TO.EnableAdvancedDataTypes)?["column_name","advanced_data_type","type","is_dttm","main_dttm_col","filterable","groupby"]:["column_name","type","is_dttm","main_dttm_col","filterable","groupby"],sortColumns:(0,p.G7)(p.TO.EnableAdvancedDataTypes)?["column_name","advanced_data_type","type","is_dttm","main_dttm_col","filterable","groupby"]:["column_name","type","is_dttm","main_dttm_col","filterable","groupby"],allowDeletes:!0,allowAddItem:r,itemGenerator:s,collection:e,columnLabelTooltips:d,stickyHeader:!0,expandFieldset:(0,X.Y)(ze,{children:(0,X.FD)(le,{compact:!0,children:[o&&(0,X.Y)(re,{fieldKey:"expression",label:(0,u.t)("SQL expression"),control:(0,X.Y)(w.A,{language:"markdown",offerEditInModal:!1,resize:"vertical"})}),(0,X.Y)(re,{fieldKey:"verbose_name",label:(0,u.t)("Label"),control:(0,X.Y)(A.A,{controlId:"verbose_name",placeholder:(0,u.t)("Label")})}),(0,X.Y)(re,{fieldKey:"description",label:(0,u.t)("Description"),control:(0,X.Y)(A.A,{controlId:"description",placeholder:(0,u.t)("Description")})}),l&&(0,X.Y)(re,{fieldKey:"type",label:(0,u.t)("Data type"),control:(0,X.Y)(k.A,{ariaLabel:(0,u.t)("Data type"),options:Ae,name:"type",allowNewOptions:!0,allowClear:!0})}),(0,p.G7)(p.TO.EnableAdvancedDataTypes)?(0,X.Y)(re,{fieldKey:"advanced_data_type",label:(0,u.t)("Advanced data type"),control:(0,X.Y)(A.A,{controlId:"advanced_data_type",placeholder:(0,u.t)("Advanced Data type")})}):(0,X.Y)(X.FK,{}),(0,X.Y)(re,{fieldKey:"python_date_format",label:(0,u.t)("Datetime format"),description:(0,X.FD)("div",{children:[(0,u.t)("The pattern of timestamp format. For strings use "),(0,X.Y)(D.o.Link,{href:"https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior",children:(0,u.t)("Python datetime string pattern")}),(0,u.t)(" expression which needs to adhere to the "),(0,X.Y)(D.o.Link,{href:"https://en.wikipedia.org/wiki/ISO_8601",children:(0,u.t)("ISO 8601")}),(0,u.t)(" standard to ensure that the lexicographical ordering\n                      coincides with the chronological ordering. If the\n                      timestamp format does not adhere to the ISO 8601 standard\n                      you will need to define an expression and type for\n                      transforming the string into a date or timestamp. Note\n                      currently time zones are not supported. If time is stored\n                      in epoch format, put `epoch_s` or `epoch_ms`. If no pattern\n                      is specified we fall back to using the optional defaults on a per\n                      database/column name level via the extra parameter.")]}),control:(0,X.Y)(A.A,{controlId:"python_date_format",placeholder:"%Y-%m-%d"})}),(0,X.Y)(re,{fieldKey:"certified_by",label:(0,u.t)("Certified By"),description:(0,u.t)("Person or group that has certified this metric"),control:(0,X.Y)(A.A,{controlId:"certified",placeholder:(0,u.t)("Certified by")})}),(0,X.Y)(re,{fieldKey:"certification_details",label:(0,u.t)("Certification details"),description:(0,u.t)("Details of the certification"),control:(0,X.Y)(A.A,{controlId:"certificationDetails",placeholder:(0,u.t)("Certification details")})})]})}),columnLabels:(0,p.G7)(p.TO.EnableAdvancedDataTypes)?{column_name:(0,u.t)("Column"),advanced_data_type:(0,u.t)("Advanced data type"),type:(0,u.t)("Data type"),groupby:(0,u.t)("Is dimension"),is_dttm:(0,u.t)("Is temporal"),main_dttm_col:(0,u.t)("Default datetime"),filterable:(0,u.t)("Is filterable")}:{column_name:(0,u.t)("Column"),type:(0,u.t)("Data type"),groupby:(0,u.t)("Is dimension"),is_dttm:(0,u.t)("Is temporal"),main_dttm_col:(0,u.t)("Default datetime"),filterable:(0,u.t)("Is filterable")},onChange:a,itemRenderers:(0,p.G7)(p.TO.EnableAdvancedDataTypes)?{column_name:(e,t,a,n)=>i?(0,X.FD)(xe,{children:[n.is_certified&&(0,X.Y)(z.T,{certifiedBy:n.certified_by,details:n.certification_details}),(0,X.Y)(I.z,{canEdit:!0,title:e,onSaveTitle:t})]}):(0,X.FD)(xe,{children:[n.is_certified&&(0,X.Y)(z.T,{certifiedBy:n.certified_by,details:n.certification_details}),e]}),main_dttm_col:(e,a,i,o)=>{const r=t.main_dttm_col===o.column_name,l=!(null!=o&&o.is_dttm);return(0,X.Y)(c.s,{"aria-label":(0,u.t)("Set %s as default datetime column",o.column_name),"data-test":`radio-default-dttm-${o.column_name}`,checked:r,disabled:l,onChange:()=>n({...t,main_dttm_col:o.column_name})})},type:e=>e?(0,X.Y)(F.JU,{children:e}):null,advanced_data_type:e=>(0,X.Y)(F.JU,{onChange:a,children:e}),is_dttm:Se,filterable:Se,groupby:Se}:{column_name:(e,t,a,n)=>i?(0,X.FD)(xe,{children:[n.is_certified&&(0,X.Y)(z.T,{certifiedBy:n.certified_by,details:n.certification_details}),(0,X.Y)(A.A,{value:e,onChange:t})]}):(0,X.FD)(xe,{children:[n.is_certified&&(0,X.Y)(z.T,{certifiedBy:n.certified_by,details:n.certification_details}),e]}),main_dttm_col:(e,a,i,o)=>{const r=t.main_dttm_col===o.column_name,l=!(null!=o&&o.is_dttm);return(0,X.Y)(c.s,{"aria-label":(0,u.t)("Set %s as default datetime column",o.column_name),"data-test":`radio-default-dttm-${o.column_name}`,checked:r,disabled:l,onChange:()=>n({...t,main_dttm_col:o.column_name})})},type:e=>e?(0,X.Y)(F.JU,{children:e}):null,is_dttm:Se,filterable:Se,groupby:Se}})}function De({label:e,formElement:t}){return(0,X.FD)("div",{children:[(0,X.Y)("div",{children:(0,X.Y)("strong",{children:e})}),(0,X.Y)("div",{children:t})]})}function ze({children:e}){return(0,X.Y)(L.Z,{padded:!0,style:{backgroundColor:m.vP.theme.colorBgLayout},children:e})}Ee.propTypes={title:s().string,collection:s().array},ke.propTypes={columns:s().array.isRequired,datasource:s().object.isRequired,onColumnsChange:s().func.isRequired,onDatasourceChange:s().func.isRequired,editableColumnName:s().bool,showExpression:s().bool,allowAddItem:s().bool,allowEditDataType:s().bool,itemGenerator:s().func},ke.defaultProps={editableColumnName:!1,showExpression:!1,allowAddItem:!1,allowEditDataType:!1,itemGenerator:()=>({column_name:(0,u.t)("<new column>"),filterable:!0,groupby:!0})},De.propTypes={label:s().string,formElement:s().node},ze.propTypes={children:s().node};const Ie={datasource:s().object.isRequired,onChange:s().func,addSuccessToast:s().func.isRequired,addDangerToast:s().func.isRequired,setIsEditing:s().func};function Fe({datasource:e,onChange:t}){const a=(0,r.useCallback)(((e="",t,a)=>{const n=o().encode({filter:e,page:t,page_size:a});return g.A.get({endpoint:`/api/v1/dataset/related/owners?q=${n}`}).then((e=>({data:e.json.result.filter((e=>e.extra.active)).map((e=>({value:e.value,label:e.text}))),totalCount:e.json.count})))}),[]);return(0,X.Y)(M.A,{ariaLabel:(0,u.t)("Select owners"),mode:"multiple",name:"owners",value:e.owners,options:a,onChange:t,header:(0,X.Y)(O.l,{children:(0,u.t)("Owners")}),allowClear:!0})}const Le=null!=(me=ue.get("sqleditor.extension.resultTable"))?me:j.TR;var Me={name:"hkh81z",styles:"margin-top:8px"},Oe={name:"hkh81z",styles:"margin-top:8px"};class qe extends r.PureComponent{constructor(e){var t;super(e),this.renderSqlEditorOverlay=()=>(0,X.Y)("div",{css:e=>n.AH`
        position: absolute;
        background: ${e.colorBgLayout};
        align-items: center;
        display: flex;
        height: 100%;
        width: 100%;
        justify-content: center;
      `,children:(0,X.FD)("div",{children:[(0,X.Y)(q.R,{position:"inline-centered"}),(0,X.Y)("span",{css:e=>n.AH`
            display: block;
            margin: ${4*e.sizeUnit}px auto;
            width: fit-content;
            color: ${e.colorText};
          `,children:(0,u.t)("We are working on your query")})]})}),this.renderSqlErrorMessage=()=>{var e;return(0,X.FD)("span",{css:e=>n.AH`
        font-size: ${e.fontSizeSM}px;
        color: ${e.colorErrorText};
      `,children:[(null==(e=this.props.database)?void 0:e.error)&&(0,u.t)("Error executing query. "),this.renderOpenInSqlLabLink(!0),(0,u.t)(" to check for details.")]})},this.state={datasource:{...e.datasource,owners:e.datasource.owners.map((e=>({value:e.value||e.id,label:e.label||`${e.first_name} ${e.last_name}`}))),metrics:null==(t=e.datasource.metrics)?void 0:t.map((e=>{const{certified_by:t,certification_details:a}=e,{certification:{details:n,certified_by:i}={},warning_markdown:o}=JSON.parse(e.extra||"{}")||{};return{...e,certification_details:a||n,warning_markdown:o||"",certified_by:i||t}}))},errors:[],isSqla:"table"===e.datasource.datasource_type||"table"===e.datasource.type,isEditMode:!1,databaseColumns:e.datasource.columns.filter((e=>!e.expression)),calculatedColumns:e.datasource.columns.filter((e=>!!e.expression)),metadataLoading:!1,activeTabKey:we,datasourceType:e.datasource.sql?$e.virtual.key:$e.physical.key},this.onChange=this.onChange.bind(this),this.onChangeEditMode=this.onChangeEditMode.bind(this),this.onDatasourcePropChange=this.onDatasourcePropChange.bind(this),this.onDatasourceChange=this.onDatasourceChange.bind(this),this.tableChangeAndSyncMetadata=this.tableChangeAndSyncMetadata.bind(this),this.syncMetadata=this.syncMetadata.bind(this),this.setColumns=this.setColumns.bind(this),this.validateAndChange=this.validateAndChange.bind(this),this.handleTabSelect=this.handleTabSelect.bind(this),this.formatSql=this.formatSql.bind(this),this.currencies=(0,b.A)(e.currencies).map((e=>({value:e,label:`${(0,f.Q)({symbol:e})} (${e})`})))}onChange(){const{datasourceType:e,datasource:t}=this.state,a=e===$e.physical.key?"":t.sql,n={...this.state.datasource,sql:a,columns:[...this.state.databaseColumns,...this.state.calculatedColumns]};this.props.onChange(n,this.state.errors)}onChangeEditMode(){this.props.setIsEditing(!this.state.isEditMode),this.setState((e=>({isEditMode:!e.isEditMode})))}onDatasourceChange(e,t=this.validateAndChange){this.setState({datasource:e},t)}onDatasourcePropChange(e,t){if(void 0===t)return;const a={...this.state.datasource,[e]:t};this.setState((a=>({datasource:{...a.datasource,[e]:t}})),"table_name"===e?this.onDatasourceChange(a,this.tableChangeAndSyncMetadata):this.onDatasourceChange(a,this.validateAndChange))}onDatasourceTypeChange(e){this.setState({datasourceType:e},this.onChange)}setColumns(e){this.setState(e,this.validateAndChange)}validateAndChange(){this.validate(this.onChange)}async onQueryRun(){this.props.runQuery({client_id:this.props.clientId,database_id:this.state.datasource.database.id,json:!0,runAsync:!1,catalog:this.state.datasource.catalog,schema:this.state.datasource.schema,sql:this.state.datasource.sql,tmp_table_name:"",select_as_cta:!1,ctas_method:"TABLE",queryLimit:25,expand_data:!0})}async onQueryFormat(){const{datasource:e}=this.state;if(e.sql&&this.state.isEditMode)try{const t=await this.props.formatQuery(e.sql);this.onDatasourcePropChange("sql",t.json.result),this.props.addSuccessToast((0,u.t)("SQL was formatted"))}catch(e){const{error:t,statusText:a}=await(0,y.h4)(e);this.props.addDangerToast(t||a||(0,u.t)("An error occurred while formatting SQL"))}}getSQLLabUrl(){return`/sqllab/?${new URLSearchParams({dbid:this.state.datasource.database.id,sql:this.state.datasource.sql,name:this.state.datasource.datasource_name,schema:this.state.datasource.schema,autorun:!0,isDataset:!0}).toString()}`}openOnSqlLab(){window.open(this.getSQLLabUrl(),"_blank","noopener,noreferrer")}tableChangeAndSyncMetadata(){this.validate((()=>{this.syncMetadata(),this.onChange()}))}async formatSql(){const{datasource:e}=this.state;if(e.sql)try{const t=await g.A.post({endpoint:"/api/v1/sql/format",body:JSON.stringify({sql:e.sql}),headers:{"Content-Type":"application/json"}});this.onDatasourcePropChange("sql",t.json.result),this.props.addSuccessToast((0,u.t)("SQL was formatted"))}catch(e){const{error:t,statusText:a}=await(0,y.h4)(e);this.props.addDangerToast(t||a||(0,u.t)("An error occurred while formatting SQL"))}}async syncMetadata(){const{datasource:e}=this.state;this.setState({metadataLoading:!0});try{const t=await async function(e){var t,a;const n={datasource_type:e.type||e.datasource_type,database_name:(null==(t=e.database)?void 0:t.database_name)||(null==(a=e.database)?void 0:a.name),catalog_name:e.catalog,schema_name:e.schema,table_name:e.table_name,normalize_columns:e.normalize_columns,always_filter_main_dttm:e.always_filter_main_dttm};Object.entries(n).forEach((([e,t])=>{void 0===t&&(n[e]=null)}));const i=`/datasource/external_metadata_by_name/?q=${o().encode_uri(n)}`,{json:r}=await g.A.get({endpoint:i});return r}(e),a=function(e,t,a){const n=t.map((e=>e.column_name)),i=e.reduce(((e,t)=>(e[t.column_name]=t,e)),{}),o={added:[],modified:[],removed:e.filter((e=>!(e.expression||n.includes(e.column_name)))).map((e=>e.column_name)),finalColumns:[]};return t.forEach((e=>{const t=i[e.column_name];t?t.type!==e.type||t.is_dttm!==e.is_dttm?(o.finalColumns.push({...t,type:e.type,is_dttm:t.is_dttm||e.is_dttm}),o.modified.push(e.column_name)):o.finalColumns.push(t):(o.finalColumns.push({id:(0,J.Ak)(),column_name:e.column_name,type:e.type,groupby:!0,filterable:!0,is_dttm:e.is_dttm}),o.added.push(e.column_name))})),e.filter((e=>e.expression)).forEach((e=>{o.finalColumns.push(e)})),o.modified.length&&a((0,u.tn)("Modified 1 column in the virtual dataset","Modified %s columns in the virtual dataset",o.modified.length,o.modified.length)),o.removed.length&&a((0,u.tn)("Removed 1 column from the virtual dataset","Removed %s columns from the virtual dataset",o.removed.length,o.removed.length)),o.added.length&&a((0,u.tn)("Added 1 new column to the virtual dataset","Added %s new columns to the virtual dataset",o.added.length,o.added.length)),o}(e.columns,t,this.props.addSuccessToast);this.setColumns({databaseColumns:a.finalColumns.filter((e=>!e.expression))}),this.props.addSuccessToast((0,u.t)("Metadata has been synced")),this.setState({metadataLoading:!1})}catch(e){const{error:t,statusText:a}=await(0,y.h4)(e);this.props.addDangerToast(t||a||(0,u.t)("An error has occurred")),this.setState({metadataLoading:!1})}}findDuplicates(e,t){const a={},n=[];return e.forEach((e=>{const i=t(e);i in a?n.push(i):a[i]=null})),n}validate(e){let t,a=[];const{datasource:n}=this.state;t=this.findDuplicates(n.columns,(e=>e.column_name)),a=a.concat(t.map((e=>(0,u.t)("Column name [%s] is duplicated",e)))),t=this.findDuplicates(n.metrics,(e=>e.metric_name)),a=a.concat(t.map((e=>(0,u.t)("Metric name [%s] is duplicated",e))));const i=this.state.calculatedColumns.filter((e=>!e.expression&&!e.json));a=a.concat(i.map((e=>(0,u.t)("Calculated column [%s] requires an expression",e.column_name))));try{var o;null==(o=this.state.datasource.metrics)||o.forEach((e=>{var t;return(null==(t=e.currency)?void 0:t.symbol)&&new Intl.NumberFormat("en-US",{style:"currency",currency:e.currency.symbol})}))}catch{a=a.concat([(0,u.t)("Invalid currency code in saved metrics")])}this.setState({errors:a},e)}handleTabSelect(e){this.setState({activeTabKey:e})}sortMetrics(e){return e.sort((({id:e},{id:t})=>t-e))}renderSettingsFieldset(){const{datasource:e}=this.state;return(0,X.FD)(le,{title:(0,u.t)("Basic"),item:e,onChange:this.onDatasourceChange,children:[(0,X.Y)(re,{fieldKey:"description",label:(0,u.t)("Description"),control:(0,X.Y)(w.A,{language:"markdown",offerEditInModal:!1,resize:"vertical"})}),(0,X.Y)(re,{fieldKey:"default_endpoint",label:(0,u.t)("Default URL"),description:(0,u.t)("Default URL to redirect to when accessing from the dataset list page.\n            Accepts relative URLs such as <span style=„white-space: nowrap;”>/superset/dashboard/{id}/</span>"),control:(0,X.Y)(A.A,{controlId:"default_endpoint"})}),(0,X.Y)(re,{inline:!0,fieldKey:"filter_select_enabled",label:(0,u.t)("Autocomplete filters"),description:(0,u.t)("Whether to populate autocomplete filters options"),control:(0,X.Y)(S.A,{})}),this.state.isSqla&&(0,X.Y)(re,{fieldKey:"fetch_values_predicate",label:(0,u.t)("Autocomplete query predicate"),description:(0,u.t)('When using "Autocomplete filters", this can be used to improve performance of the query fetching the values. Use this option to apply a predicate (WHERE clause) to the query selecting the distinct values from the table. Typically the intent would be to limit the scan by applying a relative time filter on a partitioned or indexed time-related field.'),control:(0,X.Y)(w.A,{language:"sql",controlId:"fetch_values_predicate",minLines:5,resize:"vertical"})}),this.state.isSqla&&(0,X.Y)(re,{fieldKey:"extra",label:(0,u.t)("Extra"),description:(0,u.t)('Extra data to specify table metadata. Currently supports metadata of the format: `{ "certification": { "certified_by": "Data Platform Team", "details": "This table is the source of truth." }, "warning_markdown": "This is a warning." }`.'),control:(0,X.Y)(w.A,{controlId:"extra",language:"json",offerEditInModal:!1,resize:"vertical"})}),(0,X.Y)(Fe,{datasource:e,onChange:t=>{this.onDatasourceChange({...e,owners:t})}})]})}renderAdvancedFieldset(){const{datasource:e}=this.state;return(0,X.FD)(le,{title:(0,u.t)("Advanced"),item:e,onChange:this.onDatasourceChange,children:[(0,X.Y)(re,{fieldKey:"cache_timeout",label:(0,u.t)("Cache timeout"),description:(0,u.t)("The duration of time in seconds before the cache is invalidated. Set to -1 to bypass the cache."),control:(0,X.Y)(A.A,{controlId:"cache_timeout"})}),(0,X.Y)(re,{fieldKey:"offset",label:(0,u.t)("Hours offset"),control:(0,X.Y)(A.A,{controlId:"offset"}),description:(0,u.t)("The number of hours, negative or positive, to shift the time column. This can be used to move UTC time to local time.")}),this.state.isSqla&&(0,X.Y)(re,{fieldKey:"template_params",label:(0,u.t)("Template parameters"),description:(0,u.t)("A set of parameters that become available in the query using Jinja templating syntax"),control:(0,X.Y)(A.A,{controlId:"template_params"})}),(0,X.Y)(re,{inline:!0,fieldKey:"normalize_columns",label:(0,u.t)("Normalize column names"),description:(0,u.t)("Allow column names to be changed to case insensitive format, if supported (e.g. Oracle, Snowflake)."),control:(0,X.Y)(S.A,{controlId:"normalize_columns"})}),(0,X.Y)(re,{inline:!0,fieldKey:"always_filter_main_dttm",label:(0,u.t)("Always filter main datetime column"),description:(0,u.t)("When the secondary temporal columns are filtered, apply the same filter to the main datetime column."),control:(0,X.Y)(S.A,{controlId:"always_filter_main_dttm"})})]})}renderSpatialTab(){const{datasource:e}=this.state,{spatials:t,all_cols:a}=e;return{key:"SPATIAL",label:(0,X.Y)(Ee,{collection:t,title:(0,u.t)("Spatial")}),children:(0,X.Y)(he,{tableColumns:["name","config"],onChange:this.onDatasourcePropChange.bind(this,"spatials"),itemGenerator:()=>({name:(0,u.t)("<new spatial>"),type:(0,u.t)("<no type>"),config:null}),collection:t,allowDeletes:!0,itemRenderers:{name:(e,t)=>(0,X.Y)(I.z,{canEdit:!0,title:e,onSaveTitle:t}),config:(e,t)=>(0,X.Y)(Y.A,{value:e,onChange:t,choices:a})}})}}renderOpenInSqlLabLink(e=!1){return(0,X.Y)("a",{href:this.getSQLLabUrl(),target:"_blank",rel:"noopener noreferrer",css:t=>n.AH`
          color: ${e?t.colorErrorText:t.colorText};
          font-size: ${t.fontSizeSM}px;
          text-decoration: underline;
        `,children:(0,u.t)("Open in SQL lab")})}renderSourceFieldset(){var e,t,a,i,o,r,l,s,d,h,m,p;const{datasource:g}=this.state;return(0,X.FD)("div",{children:[(0,X.FD)(ye,{children:[(0,X.Y)("span",{css:e=>n.AH`
              color: ${e.colorTextTertiary};
            `,role:"button",tabIndex:0,onClick:this.onChangeEditMode,children:this.state.isEditMode?(0,X.Y)(P.F.UnlockOutlined,{iconSize:"xl",css:e=>n.AH`
                  margin: auto ${e.sizeUnit}px auto 0;
                `}):(0,X.Y)(P.F.LockOutlined,{iconSize:"xl",css:e=>({margin:`auto ${e.sizeUnit}px auto 0`})})}),!this.state.isEditMode&&(0,X.Y)("div",{children:(0,u.t)("Click the lock to make changes.")}),this.state.isEditMode&&(0,X.Y)("div",{children:(0,u.t)("Click the lock to prevent further changes.")})]}),(0,X.Y)("div",{css:e=>n.AH`
            margin-top: ${3*e.sizeUnit}px;
          `,children:Ye.map((e=>(0,X.Y)(c.s,{value:e.key,inline:!0,onChange:this.onDatasourceTypeChange.bind(this,e.key),checked:this.state.datasourceType===e.key,disabled:!this.state.isEditMode,children:e.label},e.key)))}),(0,X.Y)(U.c,{}),(0,X.FD)(le,{item:g,onChange:this.onDatasourceChange,compact:!0,children:[this.state.datasourceType===$e.virtual.key&&(0,X.Y)("div",{children:this.state.isSqla&&(0,X.FD)(X.FK,{children:[(0,X.FD)(R.A,{xs:24,md:12,children:[(0,X.Y)(re,{fieldKey:"databaseSelector",label:(0,u.t)("Virtual"),control:(0,X.Y)("div",{css:Me,children:(0,X.Y)(V.R,{db:null==g?void 0:g.database,catalog:g.catalog,schema:g.schema,onCatalogChange:e=>this.state.isEditMode&&this.onDatasourcePropChange("catalog",e),onSchemaChange:e=>this.state.isEditMode&&this.onDatasourcePropChange("schema",e),onDbChange:e=>this.state.isEditMode&&this.onDatasourcePropChange("database",e),formMode:!1,handleError:this.props.addDangerToast,readOnly:!this.state.isEditMode})})}),(0,X.Y)("div",{css:(0,n.AH)({width:"calc(100% - 34px)",marginTop:-16},"",""),children:(0,X.Y)(re,{fieldKey:"table_name",label:(0,u.t)("Name"),control:(0,X.Y)(A.A,{controlId:"table_name",onChange:e=>{this.onDatasourcePropChange("table_name",e)},placeholder:(0,u.t)("Dataset name"),disabled:!this.state.isEditMode})})})]}),(0,X.Y)(re,{fieldKey:"sql",label:(0,u.t)("SQL"),description:(0,u.t)("When specifying SQL, the datasource acts as a view. Superset will use this statement as a subquery while grouping and filtering on the generated parent queries.If changes are made to your SQL query, columns in your dataset will be synced when saving the dataset."),control:null!=(e=this.props.database)&&e.isLoading?(0,X.FD)(X.FK,{children:[this.renderSqlEditorOverlay(),(0,X.Y)(w.A,{hotkeys:[{name:"formatQuery",key:"ctrl+shift+f",descr:(0,u.t)("Format SQL query"),func:()=>{this.onQueryFormat()}}],language:"sql",offerEditInModal:!1,minLines:10,maxLines:1/0,readOnly:!this.state.isEditMode,resize:"both"})]}):(0,X.Y)(w.A,{css:e=>n.AH`
                            margin-top: ${3*e.sizeUnit}px;
                          `,hotkeys:[{name:"formatQuery",key:"ctrl+shift+f",descr:(0,u.t)("Format SQL query"),func:()=>{this.onQueryFormat()}}],language:"sql",offerEditInModal:!1,minLines:10,maxLines:1/0,readOnly:!this.state.isEditMode,resize:"both"}),additionalControl:(0,X.FD)("div",{css:n.AH`
                          position: absolute;
                          right: 0;
                          top: 0;
                          z-index: 2;
                          display: flex;
                        `,children:[(0,X.Y)(N.$,{disabled:null==(t=this.props.database)?void 0:t.isLoading,tooltip:(0,u.t)("Open SQL Lab in a new tab"),buttonStyle:"secondary",onClick:()=>{this.openOnSqlLab()},icon:(0,X.Y)(P.F.ExportOutlined,{iconSize:"s"})}),(0,X.Y)(N.$,{disabled:null==(a=this.props.database)?void 0:a.isLoading,tooltip:(0,u.t)("Run query"),buttonStyle:"primary",onClick:()=>{this.onQueryRun()},icon:(0,X.Y)(P.F.CaretRightFilled,{iconSize:"s"})})]})}),(null==(i=this.props.database)?void 0:i.queryResult)&&(0,X.FD)(X.FK,{children:[(0,X.FD)("div",{css:e=>n.AH`
                          margin-bottom: ${e.sizeUnit}px;
                        `,children:[(0,X.Y)("span",{css:e=>n.AH`
                            color: ${e.colorText};
                            font-size: ${e.fontSizeSM}px;
                          `,children:(0,u.t)("In this view you can preview the first 25 rows. ")}),this.renderOpenInSqlLabLink(),(0,X.Y)("span",{css:e=>n.AH`
                            color: ${e.colorText};
                            font-size: ${e.fontSizeSM}px;
                          `,children:(0,u.t)(" to see details.")})]}),(0,X.Y)(Le,{data:null==(o=this.props.database)?void 0:o.queryResult.data,queryId:null==(r=this.props.database)?void 0:r.queryResult.query.id,orderedColumnKeys:null==(l=this.props.database)?void 0:l.queryResult.columns.map((e=>e.column_name)),expandedColumns:null==(s=this.props.database)?void 0:s.queryResult.expandedColumns,height:300,allowHTML:!0})]}),(null==(d=this.props.database)?void 0:d.error)&&this.renderSqlErrorMessage()]})}),this.state.datasourceType===$e.physical.key&&(0,X.Y)(R.A,{xs:24,md:12,children:this.state.isSqla&&(0,X.Y)(re,{fieldKey:"tableSelector",label:(0,u.t)("Physical"),control:(0,X.Y)("div",{css:Oe,children:(0,X.Y)(_.Ay,{clearable:!1,database:{...g.database,database_name:(null==(h=g.database)?void 0:h.database_name)||(null==(m=g.database)?void 0:m.name)},dbId:null==(p=g.database)?void 0:p.id,handleError:this.props.addDangerToast,catalog:g.catalog,schema:g.schema,sqlLabMode:!1,tableValue:g.table_name,onCatalogChange:this.state.isEditMode?e=>this.onDatasourcePropChange("catalog",e):void 0,onSchemaChange:this.state.isEditMode?e=>this.onDatasourcePropChange("schema",e):void 0,onDbChange:this.state.isEditMode?e=>this.onDatasourcePropChange("database",e):void 0,onTableSelectChange:this.state.isEditMode?e=>this.onDatasourcePropChange("table_name",e):void 0,readOnly:!this.state.isEditMode})}),description:(0,u.t)("The pointer to a physical table (or view). Keep in mind that the chart is associated to this Superset logical table, and this logical table points the physical table referenced here.")})})]})]})}renderErrors(){return this.state.errors.length>0?(0,X.Y)(B.F,{css:e=>({marginBottom:4*e.sizeUnit}),type:"error",message:(0,X.Y)(X.FK,{children:this.state.errors.map((e=>(0,X.Y)("div",{children:e},e)))})}):null}renderMetricCollection(){const{datasource:e}=this.state,{metrics:t}=e,a=null!=t&&t.length?this.sortMetrics(t):[];return(0,X.Y)(he,{tableColumns:["metric_name","verbose_name","expression"],sortColumns:["metric_name","verbose_name","expression"],columnLabels:{metric_name:(0,u.t)("Metric Key"),verbose_name:(0,u.t)("Label"),expression:(0,u.t)("SQL expression")},columnLabelTooltips:{metric_name:(0,u.t)("This field is used as a unique identifier to attach the metric to charts. It is also used as the alias in the SQL query.")},expandFieldset:(0,X.Y)(ze,{children:(0,X.FD)(le,{compact:!0,children:[(0,X.Y)(re,{fieldKey:"description",label:(0,u.t)("Description"),control:(0,X.Y)(A.A,{controlId:"description",placeholder:(0,u.t)("Description")})}),(0,X.Y)(re,{fieldKey:"d3format",label:(0,u.t)("D3 format"),control:(0,X.Y)(A.A,{controlId:"d3format",placeholder:"%y/%m/%d"})}),(0,X.Y)(re,{fieldKey:"currency",label:(0,u.t)("Metric currency"),control:(0,X.Y)(T.A,{currencySelectOverrideProps:{placeholder:(0,u.t)("Select or type currency symbol")},symbolSelectAdditionalStyles:n.AH`
                      max-width: 30%;
                    `})}),(0,X.Y)(re,{label:(0,u.t)("Certified by"),fieldKey:"certified_by",description:(0,u.t)("Person or group that has certified this metric"),control:(0,X.Y)(A.A,{controlId:"certified_by",placeholder:(0,u.t)("Certified by")})}),(0,X.Y)(re,{label:(0,u.t)("Certification details"),fieldKey:"certification_details",description:(0,u.t)("Details of the certification"),control:(0,X.Y)(A.A,{controlId:"certification_details",placeholder:(0,u.t)("Certification details")})}),(0,X.Y)(re,{label:(0,u.t)("Warning"),fieldKey:"warning_markdown",description:(0,u.t)("Optional warning about use of this metric"),control:(0,X.Y)(w.A,{controlId:"warning_markdown",language:"markdown",offerEditInModal:!1,resize:"vertical"})})]})}),collection:a,allowAddItem:!0,onChange:this.onDatasourcePropChange.bind(this,"metrics"),itemGenerator:()=>({metric_name:(0,u.t)("<new metric>"),verbose_name:"",expression:""}),itemCellProps:{expression:()=>({width:"240px"})},itemRenderers:{metric_name:(e,t,a,n)=>(0,X.FD)(ge,{children:[n.is_certified&&(0,X.Y)(z.T,{certifiedBy:n.certified_by,details:n.certification_details}),n.warning_markdown&&(0,X.Y)(C.A,{warningMarkdown:n.warning_markdown}),(0,X.Y)(I.z,{canEdit:!0,title:e,onSaveTitle:t,maxWidth:300})]}),verbose_name:(e,t)=>(0,X.Y)(A.A,{canEdit:!0,value:e,onChange:t}),expression:(e,t)=>(0,X.Y)(w.A,{canEdit:!0,initialValue:e,onChange:t,extraClasses:["datasource-sql-expression"],language:"sql",offerEditInModal:!1,minLines:5,textAreaStyles:{minWidth:"200px",maxWidth:"450px"},resize:"both"}),description:(e,t,a)=>(0,X.Y)(De,{label:a,formElement:(0,X.Y)(A.A,{value:e,onChange:t})}),d3format:(e,t,a)=>(0,X.Y)(De,{label:a,formElement:(0,X.Y)(A.A,{value:e,onChange:t})})},allowDeletes:!0,stickyHeader:!0})}render(){const{datasource:e,activeTabKey:t}=this.state,{metrics:a}=e,n=null!=a&&a.length?this.sortMetrics(a):[],{theme:i}=this.props;return(0,X.FD)(pe,{"data-test":"datasource-editor",children:[this.renderErrors(),(0,X.Y)(B.F,{css:e=>({marginBottom:4*e.sizeUnit}),type:"warning",message:(0,X.FD)(X.FK,{children:[" ",(0,X.FD)("strong",{children:[(0,u.t)("Be careful.")," "]}),(0,u.t)("Changing these settings will affect all charts using this dataset, including charts owned by other people.")]})}),(0,X.Y)(be,{id:"table-tabs","data-test":"edit-dataset-tabs",onChange:this.handleTabSelect,defaultActiveKey:t,items:[{key:we,label:(0,u.t)("Source"),children:this.renderSourceFieldset(i)},{key:"METRICS",label:(0,X.Y)(Ee,{collection:n,title:(0,u.t)("Metrics")}),children:this.renderMetricCollection()},{key:"COLUMNS",label:(0,X.Y)(Ee,{collection:this.state.databaseColumns,title:(0,u.t)("Columns")}),children:(0,X.FD)(Ce,{children:[(0,X.Y)(ve,{children:(0,X.Y)(_e,{children:(0,X.FD)(N.$,{buttonSize:"small",buttonStyle:"tertiary",onClick:this.syncMetadata,className:"sync-from-source",disabled:this.state.isEditMode,children:[(0,X.Y)(P.F.DatabaseOutlined,{iconSize:"m"}),(0,u.t)("Sync columns from source")]})})}),(0,X.Y)(ke,{className:"columns-table",columns:this.state.databaseColumns,datasource:e,onColumnsChange:e=>this.setColumns({databaseColumns:e}),onDatasourceChange:this.onDatasourceChange}),this.state.metadataLoading&&(0,X.Y)(q.R,{})]})},{key:"CALCULATED_COLUMNS",label:(0,X.Y)(Ee,{collection:this.state.calculatedColumns,title:(0,u.t)("Calculated columns")}),children:(0,X.Y)(Ce,{children:(0,X.Y)(ke,{columns:this.state.calculatedColumns,onColumnsChange:e=>this.setColumns({calculatedColumns:e}),columnLabelTooltips:{column_name:(0,u.t)("This field is used as a unique identifier to attach the calculated dimension to charts. It is also used as the alias in the SQL query.")},onDatasourceChange:this.onDatasourceChange,datasource:e,editableColumnName:!0,showExpression:!0,allowAddItem:!0,allowEditDataType:!0,itemGenerator:()=>({column_name:(0,u.t)("<new column>"),filterable:!0,groupby:!0,expression:(0,u.t)("<enter SQL expression here>"),expanded:!0})})})},{key:"SETTINGS",label:(0,u.t)("Settings"),children:(0,X.FD)(K.A,{gutter:16,children:[(0,X.Y)(R.A,{xs:24,md:12,children:(0,X.Y)(ze,{children:this.renderSettingsFieldset()})}),(0,X.Y)(R.A,{xs:24,md:12,children:(0,X.Y)(ze,{children:this.renderAdvancedFieldset()})})]})}]})]})}componentDidMount(){G().bind("ctrl+shift+f",(e=>(e.preventDefault(),this.state.isEditMode&&this.onQueryFormat(),!1)))}componentWillUnmount(){G().unbind("ctrl+shift+f"),this.props.resetQuery()}}qe.defaultProps={onChange:()=>{},setIsEditing:()=>{}},qe.propTypes=Ie;const Pe=(0,v.b)(qe),Ue=(0,$.Ay)((0,d.Ng)((e=>({database:null==e?void 0:e.database})),(e=>({runQuery:t=>e(function(e){return async function(t){try{t(Q(!0)),t({type:"SET_QUERY_RESULT",payload:await H(e)})}catch(e){t(function(e){return{type:"SET_QUERY_ERROR",payload:e}}(e.message))}finally{t(Q(!1))}}}(t)),resetQuery:()=>e({type:"RESET_DATABASE_STATE"}),formatQuery:t=>e(function(e){return function(t){return g.A.post({endpoint:"/api/v1/sqllab/format_sql/",body:JSON.stringify({sql:e}),headers:{"Content-Type":"application/json"}}).then((e=>(t({type:"SET_QUERY",payload:e.json.result}),e)))}}(t))})))(Pe))}}]);