"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[3542],{16370:(e,t,n)=>{n.d(t,{A:()=>i});const i=n(26606).A},36552:(e,t,n)=>{n.d(t,{A:()=>u});var i=n(96540),r=n(46942),o=n.n(r),l=n(62279),a=n(829),d=n(77132),s=n(25905),c=n(37358),h=n(14277);const p=e=>{const{componentCls:t}=e;return{[t]:{"&-horizontal":{[`&${t}`]:{"&-sm":{marginBlock:e.marginXS},"&-md":{marginBlock:e.margin}}}}}},m=e=>{const{componentCls:t,sizePaddingEdgeHorizontal:n,colorSplit:i,lineWidth:r,textPaddingInline:o,orientationMargin:l,verticalMarginInline:a}=e;return{[t]:Object.assign(Object.assign({},(0,s.dF)(e)),{borderBlockStart:`${(0,d.zA)(r)} solid ${i}`,"&-vertical":{position:"relative",top:"-0.06em",display:"inline-block",height:"0.9em",marginInline:a,marginBlock:0,verticalAlign:"middle",borderTop:0,borderInlineStart:`${(0,d.zA)(r)} solid ${i}`},"&-horizontal":{display:"flex",clear:"both",width:"100%",minWidth:"100%",margin:`${(0,d.zA)(e.marginLG)} 0`},[`&-horizontal${t}-with-text`]:{display:"flex",alignItems:"center",margin:`${(0,d.zA)(e.dividerHorizontalWithTextGutterMargin)} 0`,color:e.colorTextHeading,fontWeight:500,fontSize:e.fontSizeLG,whiteSpace:"nowrap",textAlign:"center",borderBlockStart:`0 ${i}`,"&::before, &::after":{position:"relative",width:"50%",borderBlockStart:`${(0,d.zA)(r)} solid transparent`,borderBlockStartColor:"inherit",borderBlockEnd:0,transform:"translateY(50%)",content:"''"}},[`&-horizontal${t}-with-text-start`]:{"&::before":{width:`calc(${l} * 100%)`},"&::after":{width:`calc(100% - ${l} * 100%)`}},[`&-horizontal${t}-with-text-end`]:{"&::before":{width:`calc(100% - ${l} * 100%)`},"&::after":{width:`calc(${l} * 100%)`}},[`${t}-inner-text`]:{display:"inline-block",paddingBlock:0,paddingInline:o},"&-dashed":{background:"none",borderColor:i,borderStyle:"dashed",borderWidth:`${(0,d.zA)(r)} 0 0`},[`&-horizontal${t}-with-text${t}-dashed`]:{"&::before, &::after":{borderStyle:"dashed none none"}},[`&-vertical${t}-dashed`]:{borderInlineStartWidth:r,borderInlineEnd:0,borderBlockStart:0,borderBlockEnd:0},"&-dotted":{background:"none",borderColor:i,borderStyle:"dotted",borderWidth:`${(0,d.zA)(r)} 0 0`},[`&-horizontal${t}-with-text${t}-dotted`]:{"&::before, &::after":{borderStyle:"dotted none none"}},[`&-vertical${t}-dotted`]:{borderInlineStartWidth:r,borderInlineEnd:0,borderBlockStart:0,borderBlockEnd:0},[`&-plain${t}-with-text`]:{color:e.colorText,fontWeight:"normal",fontSize:e.fontSize},[`&-horizontal${t}-with-text-start${t}-no-default-orientation-margin-start`]:{"&::before":{width:0},"&::after":{width:"100%"},[`${t}-inner-text`]:{paddingInlineStart:n}},[`&-horizontal${t}-with-text-end${t}-no-default-orientation-margin-end`]:{"&::before":{width:"100%"},"&::after":{width:0},[`${t}-inner-text`]:{paddingInlineEnd:n}}})}},g=(0,c.OF)("Divider",(e=>{const t=(0,h.oX)(e,{dividerHorizontalWithTextGutterMargin:e.margin,sizePaddingEdgeHorizontal:0});return[m(t),p(t)]}),(e=>({textPaddingInline:"1em",orientationMargin:.05,verticalMarginInline:e.marginXS})),{unitless:{orientationMargin:!0}});const f={small:"sm",middle:"md"},u=e=>{const{getPrefixCls:t,direction:n,className:r,style:d}=(0,l.TP)("divider"),{prefixCls:s,type:c="horizontal",orientation:h="center",orientationMargin:p,className:m,rootClassName:u,children:b,dashed:v,variant:$="solid",plain:x,style:w,size:z}=e,S=function(e,t){var n={};for(var i in e)Object.prototype.hasOwnProperty.call(e,i)&&t.indexOf(i)<0&&(n[i]=e[i]);if(null!=e&&"function"==typeof Object.getOwnPropertySymbols){var r=0;for(i=Object.getOwnPropertySymbols(e);r<i.length;r++)t.indexOf(i[r])<0&&Object.prototype.propertyIsEnumerable.call(e,i[r])&&(n[i[r]]=e[i[r]])}return n}(e,["prefixCls","type","orientation","orientationMargin","className","rootClassName","children","dashed","variant","plain","style","size"]),y=t("divider",s),[C,k,F]=g(y),I=(0,a.A)(z),A=f[I],O=!!b,M=i.useMemo((()=>"left"===h?"rtl"===n?"end":"start":"right"===h?"rtl"===n?"start":"end":h),[n,h]),E="start"===M&&null!=p,Y="end"===M&&null!=p,B=o()(y,r,k,F,`${y}-${c}`,{[`${y}-with-text`]:O,[`${y}-with-text-${M}`]:O,[`${y}-dashed`]:!!v,[`${y}-${$}`]:"solid"!==$,[`${y}-plain`]:!!x,[`${y}-rtl`]:"rtl"===n,[`${y}-no-default-orientation-margin-start`]:E,[`${y}-no-default-orientation-margin-end`]:Y,[`${y}-${A}`]:!!A},m,u),D=i.useMemo((()=>"number"==typeof p?p:/^\d+$/.test(p)?Number(p):p),[p]),N={marginInlineStart:E?D:void 0,marginInlineEnd:Y?D:void 0};return C(i.createElement("div",Object.assign({className:B,style:Object.assign(Object.assign({},d),w)},S,{role:"separator"}),b&&"vertical"!==c&&i.createElement("span",{className:`${y}-inner-text`,style:N},b)))}},47152:(e,t,n)=>{n.d(t,{A:()=>i});const i=n(32915).A},50317:(e,t,n)=>{n.d(t,{A:()=>p});var i=n(2445),r=n(17437),o=n(72234),l=n(95579),a=n(97470),d=n(18062),s=n(62799),c=n(38380);const h=r.AH`
  &.anticon {
    font-size: unset;
    .anticon {
      line-height: unset;
      vertical-align: unset;
    }
  }
`,p=({name:e,label:t,description:n,validationErrors:p=[],renderTrigger:m=!1,rightNode:g,leftNode:f,onClick:u,hovered:b=!1,tooltipOnClick:v=()=>{},warning:$,danger:x})=>{const w=(0,o.DP)();return t?(0,i.FD)("div",{className:"ControlHeader","data-test":`${e}-header`,children:[(0,i.Y)("div",{className:"pull-left",children:(0,i.FD)(s.l,{css:e=>r.AH`
            margin-bottom: ${.5*e.sizeUnit}px;
            position: relative;
            font-size: ${e.fontSizeSM}px;
          `,htmlFor:e,children:[f&&(0,i.FD)("span",{children:[f," "]}),(0,i.Y)("span",{role:"button",tabIndex:0,onClick:u,style:{cursor:u?"pointer":""},children:t})," ",$&&(0,i.FD)("span",{children:[(0,i.Y)(a.m,{id:"error-tooltip",placement:"top",title:$,children:(0,i.Y)(c.F.WarningOutlined,{iconColor:w.colorWarning,css:r.AH`
                    vertical-align: baseline;
                  `,iconSize:"s"})})," "]}),x&&(0,i.FD)("span",{children:[(0,i.Y)(a.m,{id:"error-tooltip",placement:"top",title:x,children:(0,i.Y)(c.F.CloseCircleOutlined,{iconColor:w.colorErrorText,iconSize:"s"})})," "]}),(null==p?void 0:p.length)>0&&(0,i.FD)("span",{"data-test":"error-tooltip",children:[(0,i.Y)(a.m,{id:"error-tooltip",placement:"top",title:null==p?void 0:p.join(" "),children:(0,i.Y)(c.F.CloseCircleOutlined,{iconColor:w.colorErrorText})})," "]}),b?(0,i.FD)("span",{css:()=>r.AH`
          position: absolute;
          top: 60%;
          right: 0;
          padding-left: ${w.sizeUnit}px;
          transform: translate(100%, -50%);
          white-space: nowrap;
        `,children:[n&&(0,i.FD)("span",{children:[(0,i.Y)(a.m,{id:"description-tooltip",title:n,placement:"top",children:(0,i.Y)(c.F.InfoCircleOutlined,{css:h,onClick:v})})," "]}),m&&(0,i.FD)("span",{children:[(0,i.Y)(d.I,{label:(0,l.t)("bolt"),tooltip:(0,l.t)("Changing this control takes effect instantly"),placement:"top",type:"notice"})," "]})]}):null]})}),g&&(0,i.Y)("div",{className:"pull-right",children:g}),(0,i.Y)("div",{className:"clearfix"})]}):null}},56268:(e,t,n)=>{n.d(t,{e:()=>r});var i=n(89467);const r=(0,n(72234).I4)(i.A.Item)`
  ${({theme:e})=>`\n    &.ant-form-item > .ant-row > .ant-form-item-label {\n      padding-bottom: ${e.paddingXXS}px;\n    }\n    .ant-form-item-label {\n      & > label {\n        font-size: ${e.fontSizeSM}px;\n        &.ant-form-item-required:not(.ant-form-item-required-mark-optional) {\n          &::before {\n            display: none;\n          }\n          &::after {\n            display: inline-block;\n            visibility: visible;\n            color: ${e.colorError};\n            font-size: ${e.fontSizeSM}px;\n            content: '*';\n          }\n        }\n      }\n    }\n    .ant-form-item-extra {\n      margin-top: ${e.sizeUnit}px;\n      font-size: ${e.fontSizeSM}px;\n    }\n  `}
`},67874:(e,t,n)=>{n.d(t,{Mo:()=>a,YH:()=>o,j3:()=>l});var i=n(72234),r=n(56268);const o=0,l=i.I4.div`
  min-height: ${({height:e})=>e}px;
  width: ${({width:e})=>e===o?"100%":`${e}px`};
`,a=((0,i.I4)(r.e)`
  &.ant-row.ant-form-item {
    margin: 0;
  }
`,i.I4.div`
  color: ${({theme:e,status:t="error"})=>{var n;return"help"===t?e.colors.grayscale.light1:null==(n=e.colors[t])?void 0:n.base}};
  text-align: ${({centerText:e})=>e?"center":"left"};
  width: 100%;
`)},87615:(e,t,n)=>{n.r(t),n.d(t,{default:()=>p});var i=n(2445),r=n(72234),o=n(72391),l=n(96627),a=n(96540),d=n(39074),s=n(67874);const c=(0,r.I4)(s.j3)`
  display: flex;
  align-items: center;
  overflow-x: auto;

  & .ant-tag {
    margin-right: 0;
  }
`,h=r.I4.div`
  display: flex;
  height: 100%;
  max-width: 100%;
  width: 100%;
  & > div,
  & > div:hover {
    ${({validateStatus:e,theme:t})=>{var n;return e&&`border-color: ${null==(n=t.colors[e])?void 0:n.base}`}}
  }
  & > div {
    width: 100%;
  }
`;function p(e){var t;const{setDataMask:n,setHoveredFilter:r,unsetHoveredFilter:s,setFocusedFilter:p,unsetFocusedFilter:m,setFilterActive:g,width:f,height:u,filterState:b,inputRef:v,isOverflowingFilterBar:$=!1}=e,x=(0,o.a)().get("filter.dateFilterControl"),w=null!=x?x:d.Ay,z=(0,a.useCallback)((e=>{const t=e&&e!==l.WC;n({extraFormData:t?{time_range:e}:{},filterState:{value:t?e:void 0}})}),[n]);return(0,a.useEffect)((()=>{z(b.value)}),[b.value]),null!=(t=e.formData)&&t.inView?(0,i.Y)(c,{width:f,height:u,children:(0,i.Y)(h,{ref:v,validateStatus:b.validateStatus,onFocus:p,onBlur:m,onMouseEnter:r,onMouseLeave:s,children:(0,i.Y)(w,{value:b.value||l.WC,name:e.formData.nativeFilterId||"time_range",onChange:z,onOpenPopover:()=>g(!0),onClosePopover:()=>{g(!1),s(),m()},isOverflowingFilterBar:$})})}):null}}}]);