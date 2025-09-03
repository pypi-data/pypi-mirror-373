"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[960],{25627:(e,t,i)=>{i.d(t,{x:()=>s});var l=i(2445),r=i(38380),n=i(72234),a=i(95579),o=i(82537);const s=({isPublished:e,onClick:t})=>{const i=(0,n.DP)(),s=e?(0,a.t)("Published"):(0,a.t)("Draft"),c=e?(0,l.Y)(r.F.CheckCircleOutlined,{iconSize:"s",iconColor:i.colorSuccess}):(0,l.Y)(r.F.MinusCircleOutlined,{iconSize:"s",iconColor:i.colorPrimary}),d=e?"success":"primary";return(0,l.Y)(o.JU,{type:d,icon:c,onClick:t,children:s})}},27395:(e,t,i)=>{i.d(t,{T:()=>h});var l=i(2445),r=i(72234),n=i(95579),a=i(96540),o=i(62799),s=i(17355),c=i(84335);const d=r.I4.div`
  padding-top: 8px;
  width: 50%;
  label {
    color: ${({theme:e})=>e.colors.grayscale.base};
  }
`;function h({description:e,onConfirm:t,onHide:i,open:r,title:h,name:p}){const[u,f]=(0,a.useState)(!0),[m,b]=(0,a.useState)(""),g=(0,a.useRef)(null);(0,a.useEffect)((()=>{r&&g.current&&g.current.focus()}),[r]);const F=()=>{b(""),t()};return(0,l.FD)(c.aF,{disablePrimaryButton:u,onHide:()=>{b(""),i()},onHandledPrimaryAction:F,primaryButtonName:(0,n.t)("Delete"),primaryButtonStyle:"danger",show:r,name:p,title:h,centered:!0,children:[e,(0,l.FD)(d,{children:[(0,l.Y)(o.l,{htmlFor:"delete",children:(0,n.t)('Type "%s" to confirm',(0,n.t)("DELETE"))}),(0,l.Y)(s.A,{"data-test":"delete-modal-input",type:"text",id:"delete",autoComplete:"off",value:m,onChange:e=>{var t;const i=null!=(t=e.target.value)?t:"";f(i.toUpperCase()!==(0,n.t)("DELETE")),b(i)},onPressEnter:()=>{u||F()},ref:g})]})]})}},39338:(e,t,i)=>{i.d(t,{$:()=>s});var l=i(2445),r=i(96540),n=i(72234),a=i(5362);const o=n.I4.div`
  background-image: url(${({src:e})=>e});
  background-size: cover;
  background-position: center ${({position:e})=>e};
  display: inline-block;
  height: calc(100% - 1px);
  width: calc(100% - 2px);
  margin: 1px 1px 0 1px;
`;function s({src:e,fallback:t,isLoading:i,position:n,...s}){const[c,d]=(0,r.useState)(t);return(0,r.useEffect)((()=>(e&&fetch(e).then((e=>e.blob())).then((e=>{if(/image/.test(e.type)){const t=URL.createObjectURL(e);d(t)}})).catch((e=>{a.A.error(e),d(t)})),()=>{d(t)})),[e,t]),(0,l.Y)(o,{"data-test":"image-loader",src:i?t:c,...s,position:n})}},39339:(e,t,i)=>{i.d(t,{u:()=>r});var l=i(38708);function r(e){return`${(0,l.KX)()}${e.startsWith("/")?e:`/${e}`}`}},41933:(e,t,i)=>{i.d(t,{$:()=>h});var l=i(2445),r=i(96540),n=i(72234),a=i(17437),o=i(95579),s=i(38380),c=i(97470);const d=n.I4.a`
  ${({theme:e})=>a.AH`
    font-size: ${e.fontSizeXL}px;
    display: flex;
    padding: 0 0 0 ${2*e.sizeUnit}px;
  `};
`,h=({itemId:e,isStarred:t,showTooltip:i,saveFaveStar:a,fetchFaveStar:h})=>{const p=(0,n.DP)();(0,r.useEffect)((()=>{null==h||h(e)}),[h,e]);const u=(0,r.useCallback)((i=>{i.preventDefault(),a(e,!!t)}),[t,e,a]),f=(0,l.Y)(d,{href:"#",onClick:u,className:"fave-unfave-icon","data-test":"fave-unfave-icon",role:"button",children:t?(0,l.Y)(s.F.StarFilled,{"aria-label":"starred",iconSize:"l",iconColor:p.colorWarning,name:"favorite-selected"}):(0,l.Y)(s.F.StarOutlined,{"aria-label":"unstarred",iconSize:"l",iconColor:p.colorTextTertiary,name:"favorite-unselected"})});return i?(0,l.Y)(c.m,{id:"fave-unfave-tooltip",title:(0,o.t)("Click to favorite/unfavorite"),children:f}):f}},42944:(e,t,i)=>{i.d(t,{Ay:()=>u,Fq:()=>p});var l=i(2445),r=i(96540),n=i(45738),a=i(10286),o=i(77457),s=i(72234);const c=new Set,d={sql:()=>i.e(8360).then(i.bind(i,78360)),htmlbars:()=>i.e(9633).then(i.bind(i,69633)),markdown:()=>i.e(8143).then(i.bind(i,8143)),json:()=>i.e(9172).then(i.bind(i,69172))},h=async e=>{if(!c.has(e))try{const t=await d[e]();n.A.registerLanguage(e,t.default),c.add(e)}catch(t){console.warn(`Failed to load language ${e}:`,t)}},p=async e=>{const t=e.filter((e=>!c.has(e))).map(h);await Promise.all(t)},u=({children:e,language:t="sql",customStyle:i={},showLineNumbers:d=!1,wrapLines:p=!0,style:u})=>{const[f,m]=(0,r.useState)(c.has(t));(0,r.useEffect)((()=>{(async()=>{c.has(t)||(await h(t),m(!0))})()}),[t]);const b=s.vP.isThemeDark(),g=u||(b?o.A:a.A),F={background:s.vP.theme.colorBgElevated,padding:4*s.vP.theme.sizeUnit,border:0,borderRadius:s.vP.theme.borderRadius,...i};return f?(0,l.Y)(n.A,{language:t,style:g,customStyle:F,showLineNumbers:d,wrapLines:p,children:e}):(0,l.Y)("pre",{style:{...F,fontFamily:"monospace",whiteSpace:"pre-wrap",margin:0},children:e})}},50317:(e,t,i)=>{i.d(t,{A:()=>p});var l=i(2445),r=i(17437),n=i(72234),a=i(95579),o=i(97470),s=i(18062),c=i(62799),d=i(38380);const h=r.AH`
  &.anticon {
    font-size: unset;
    .anticon {
      line-height: unset;
      vertical-align: unset;
    }
  }
`,p=({name:e,label:t,description:i,validationErrors:p=[],renderTrigger:u=!1,rightNode:f,leftNode:m,onClick:b,hovered:g=!1,tooltipOnClick:F=()=>{},warning:v,danger:x})=>{const C=(0,n.DP)();return t?(0,l.FD)("div",{className:"ControlHeader","data-test":`${e}-header`,children:[(0,l.Y)("div",{className:"pull-left",children:(0,l.FD)(c.l,{css:e=>r.AH`
            margin-bottom: ${.5*e.sizeUnit}px;
            position: relative;
            font-size: ${e.fontSizeSM}px;
          `,htmlFor:e,children:[m&&(0,l.FD)("span",{children:[m," "]}),(0,l.Y)("span",{role:"button",tabIndex:0,onClick:b,style:{cursor:b?"pointer":""},children:t})," ",v&&(0,l.FD)("span",{children:[(0,l.Y)(o.m,{id:"error-tooltip",placement:"top",title:v,children:(0,l.Y)(d.F.WarningOutlined,{iconColor:C.colorWarning,css:r.AH`
                    vertical-align: baseline;
                  `,iconSize:"s"})})," "]}),x&&(0,l.FD)("span",{children:[(0,l.Y)(o.m,{id:"error-tooltip",placement:"top",title:x,children:(0,l.Y)(d.F.CloseCircleOutlined,{iconColor:C.colorErrorText,iconSize:"s"})})," "]}),(null==p?void 0:p.length)>0&&(0,l.FD)("span",{"data-test":"error-tooltip",children:[(0,l.Y)(o.m,{id:"error-tooltip",placement:"top",title:null==p?void 0:p.join(" "),children:(0,l.Y)(d.F.CloseCircleOutlined,{iconColor:C.colorErrorText})})," "]}),g?(0,l.FD)("span",{css:()=>r.AH`
          position: absolute;
          top: 60%;
          right: 0;
          padding-left: ${C.sizeUnit}px;
          transform: translate(100%, -50%);
          white-space: nowrap;
        `,children:[i&&(0,l.FD)("span",{children:[(0,l.Y)(o.m,{id:"description-tooltip",title:i,placement:"top",children:(0,l.Y)(d.F.InfoCircleOutlined,{css:h,onClick:F})})," "]}),u&&(0,l.FD)("span",{children:[(0,l.Y)(s.I,{label:(0,a.t)("bolt"),tooltip:(0,a.t)("Changing this control takes effect instantly"),placement:"top",type:"notice"})," "]})]}):null]})}),f&&(0,l.Y)("div",{className:"pull-right",children:f}),(0,l.Y)("div",{className:"clearfix"})]}):null}},69088:(e,t,i)=>{var l;i.d(t,{U:()=>l}),function(e){e[e.Custom=1]="Custom",e[e.Type=2]="Type",e[e.Owner=3]="Owner",e[e.FavoritedBy=4]="FavoritedBy"}(l||(l={}))},73312:(e,t,i)=>{i.d(t,{A:()=>P});var l=i(90179),r=i.n(l),n=i(2445),a=i(96540),o=i(75086),s=i.n(o),c=i(52219),d=i(29221),h=i(84335),p=i(47152),u=i(16370),f=i(64658),m=i(56268),b=i(25729),g=i(15509),F=i(17355),v=i(38380),x=i(58561),C=i.n(x),y=i(72234),S=i(95579),w=i(76968),Y=i(51436),k=i(35742),$=i(62952),A=i(27366),T=i(17437),z=i(76125);const N=({colorScheme:e,hasCustomLabelsColor:t=!1,hovered:i=!1,onChange:l=()=>{}})=>{const[r,o]=(0,a.useState)([]),[s,c]=(0,a.useState)({});return(0,a.useEffect)((()=>{const e=(0,w.A)();o(e.keys().map((e=>[e,e]))),c(e.getMap())}),[]),(0,n.Y)(z.A,{description:(0,S.t)("Any color palette selected here will override the colors applied to this dashboard's individual charts"),name:"color_scheme",onChange:l,value:null!=e?e:"",choices:r,clearable:!0,hovered:i,schemes:s,hasCustomLabelsColor:t})};var D=i(99813),O=i(5261),I=i(97567),E=i(97183),U=i(55556),M=i(25106),L=i(61225),j=i(72173),_=i(35839),R=i(70856);const H=(0,y.I4)(c.iN)`
  border-radius: ${({theme:e})=>e.borderRadius}px;
  border: 1px solid ${({theme:e})=>e.colorPrimaryBorder};
`,P=(0,O.Ay)((({addSuccessToast:e,addDangerToast:t,colorScheme:i,dashboardId:l,dashboardInfo:o,dashboardTitle:x,onHide:y=()=>{},onlyApply:z=!1,onSubmit:O=()=>{},show:P=!1})=>{const B=(0,L.wA)(),[q]=d.l.useForm(),[K,V]=(0,a.useState)(!1),[W,J]=(0,a.useState)(!1),[Z,G]=(0,a.useState)(i),[Q,X]=(0,a.useState)(""),[ee,te]=(0,a.useState)(),[ie,le]=(0,a.useState)([]),[re,ne]=(0,a.useState)([]),ae=z?(0,S.t)("Apply"):(0,S.t)("Save"),[oe,se]=(0,a.useState)([]),ce=(0,w.A)(),de=(0,a.useRef)({}),he=(0,a.useMemo)((()=>oe.map((e=>({value:e.id,label:e.name})))),[oe.length]),pe=async e=>{const{error:t,statusText:i,message:l}=await(0,Y.h4)(e);let r=t||i||(0,S.t)("An error has occurred");"object"==typeof l&&"json_metadata"in l?r=l.json_metadata:"string"==typeof l&&(r=l,"Forbidden"===l&&(r=(0,S.t)("You do not have permission to edit this dashboard"))),h.aF.error({title:(0,S.t)("Error"),content:r,okButtonProps:{danger:!0,className:"btn-danger"}})},ue=(0,a.useCallback)(((e="owners",t="",i,l)=>{const r=C().encode({filter:t,page:i,page_size:l});return k.A.get({endpoint:`/api/v1/dashboard/related/${e}?q=${r}`}).then((e=>({data:e.json.result.filter((e=>void 0===e.extra.active||e.extra.active)).map((e=>({value:e.value,label:e.text}))),totalCount:e.json.count})))}),[]),fe=(0,a.useCallback)((e=>{const{id:t,dashboard_title:i,slug:l,certified_by:n,certification_details:a,owners:o,roles:c,metadata:d,is_managed_externally:h}=e,p={id:t,title:i,slug:l||"",certifiedBy:n||"",certificationDetails:a||"",isManagedExternally:h||!1,metadata:d};q.setFieldsValue(p),te(p),le(o),ne(c),G(d.color_scheme);const u=r()(d,["positions","shared_label_colors","map_label_colors","color_scheme_domain"]);X(u?s()(u):""),de.current=d}),[q]),me=(0,a.useCallback)((()=>{V(!0),k.A.get({endpoint:`/api/v1/dashboard/${l}`}).then((e=>{var t;const i=e.json.result,l=null!=(t=i.json_metadata)&&t.length?JSON.parse(i.json_metadata):{};fe({...i,metadata:l}),V(!1)}),pe)}),[l,fe]),be=()=>{try{return null!=Q&&Q.length?JSON.parse(Q):{}}catch(e){return{}}},ge=e=>{const t=(0,$.A)(e).map((e=>({id:e.value,full_name:e.label})));le(t)},Fe=e=>{const t=(0,$.A)(e).map((e=>({id:e.value,name:e.label})));ne(t)},ve=()=>(ie||[]).map((e=>({value:e.id,label:(0,M.A)(e)}))),xe=()=>y(),Ce=(e="",{updateMetadata:t=!0}={})=>{const i=ce.keys(),l=be();if(e&&!i.includes(e))throw h.aF.error({title:(0,S.t)("Error"),content:(0,S.t)("A valid color scheme is required"),okButtonProps:{danger:!0,className:"btn-danger"}}),y(),new Error("A valid color scheme is required");l.color_scheme=e,l.label_colors=l.label_colors||{},G(e),B((0,j.r7)(e)),t&&X(s()(l))};return(0,a.useEffect)((()=>{P&&(o?fe(o):me()),c.iN.preload()}),[o,me,fe,P]),(0,a.useEffect)((()=>{x&&ee&&ee.title!==x&&q.setFieldsValue({...ee,title:x})}),[ee,x,q]),(0,a.useEffect)((()=>{if((0,A.G7)(A.TO.TaggingSystem))try{(0,I.un)({objectType:I.iQ.DASHBOARD,objectId:l,includeTypes:!1},(e=>se(e)),(e=>{t(`Error fetching tags: ${e.text}`)}))}catch(e){pe(e)}}),[l]),(0,n.Y)(h.aF,{show:P,onHide:xe,title:(0,n.Y)(R.r,{isEditMode:!0,title:(0,S.t)("Dashboard properties")}),footer:(0,n.FD)(n.FK,{children:[(0,n.Y)(g.$,{htmlType:"button",buttonSize:"small",buttonStyle:"secondary",onClick:xe,"data-test":"properties-modal-cancel-button",cta:!0,children:(0,S.t)("Cancel")}),(0,n.Y)(g.$,{"data-test":"properties-modal-apply-button",onClick:q.submit,buttonSize:"small",buttonStyle:"primary",cta:!0,disabled:null==ee?void 0:ee.isManagedExternally,tooltip:null!=ee&&ee.isManagedExternally?(0,S.t)("This dashboard is managed externally, and can't be edited in Superset"):"",children:ae})]}),responsive:!0,children:(0,n.FD)(d.l,{form:q,onFinish:()=>{var r,n,a,o;const{title:c,slug:d,certifiedBy:h,certificationDetails:p}=q.getFieldsValue();let u,f=Q;try{if(!f.startsWith("{")||!f.endsWith("}"))throw new Error;u=JSON.parse(f)}catch(e){return void t((0,S.t)("JSON metadata is invalid!"))}const m=(0,U.Z6)(null==(r=u)?void 0:r.color_namespace),b=(null==(n=u)?void 0:n.color_scheme)||Z,g=b!==de.current.color_scheme,F=!(0,_.r$)(de.current.label_colors||{},(null==(a=u)?void 0:a.label_colors)||{}),v=Object.keys((null==(o=u)?void 0:o.label_colors)||{}),x=Object.keys(de.current.label_colors||{}),C=v.length>0?v:x,w=!!(F&&C.length>0)&&C,Y=be().label_colors||{},$={...de.current,label_colors:Y,color_scheme:b};de.current=$,(0,U.D2)($,g||w),B((0,j.Qn)({...$,map_label_colors:(0,U.xV)(Y)})),Ce(b,{updateMetadata:!1}),f=s()(u);const T={},N={};(0,A.G7)(A.TO.DashboardRbac)&&(T.roles=re,N.roles=(re||[]).map((e=>e.id))),(0,A.G7)(A.TO.TaggingSystem)&&(T.tags=oe,N.tags=oe.map((e=>e.id)));const D={id:l,title:c,slug:d,jsonMetadata:f,owners:ie,colorScheme:i,colorNamespace:m,certifiedBy:h,certificationDetails:p,...T};z?(O(D),y(),e((0,S.t)("Dashboard properties updated"))):k.A.put({endpoint:`/api/v1/dashboard/${l}`,headers:{"Content-Type":"application/json"},body:JSON.stringify({dashboard_title:c,slug:d||null,json_metadata:f||null,owners:(ie||[]).map((e=>e.id)),certified_by:h||null,certification_details:h&&p?p:null,...N})}).then((()=>{O(D),y(),e((0,S.t)("The dashboard has been saved"))}),pe)},"data-test":"dashboard-edit-properties-form",layout:"vertical",initialValues:ee,children:[(0,n.Y)(p.A,{children:(0,n.Y)(u.A,{xs:24,md:24,children:(0,n.Y)(f.o.Title,{level:4,children:(0,S.t)("Basic information")})})}),(0,n.FD)(p.A,{gutter:16,children:[(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("Name"),name:"title",extra:(0,S.t)("A readable URL for your dashboard"),children:(0,n.Y)(F.A,{"data-test":"dashboard-title-input",type:"text",disabled:K})})}),(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("URL slug"),name:"slug",children:(0,n.Y)(F.A,{type:"text",disabled:K})})})]}),(0,A.G7)(A.TO.DashboardRbac)?(()=>{const e=be(),t=!!Object.keys((null==e?void 0:e.label_colors)||{}).length;return(0,n.FD)(n.FK,{children:[(0,n.Y)(p.A,{children:(0,n.Y)(u.A,{xs:24,md:24,children:(0,n.Y)(f.o.Title,{level:4,style:{marginTop:"1em"},children:(0,S.t)("Access")})})}),(0,n.FD)(p.A,{gutter:16,children:[(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("Owners"),extra:(0,S.t)("Owners is a list of users who can alter the dashboard. Searchable by name or username."),children:(0,n.Y)(b.A,{allowClear:!0,allowNewOptions:!0,ariaLabel:(0,S.t)("Owners"),disabled:K,mode:"multiple",onChange:ge,options:(e,t,i)=>ue("owners",e,t,i),value:ve()})})}),(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("Roles"),extra:"Roles is a list which defines access to the dashboard. Granting a role access to a dashboard will bypass dataset level checks. If no roles are defined, regular access permissions apply.",children:(0,n.Y)(b.A,{allowClear:!0,ariaLabel:(0,S.t)("Roles"),disabled:K,mode:"multiple",onChange:Fe,options:(e,t,i)=>ue("roles",e,t,i),value:(re||[]).map((e=>({value:e.id,label:`${e.name}`})))})})})]}),(0,n.Y)(p.A,{children:(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(N,{hasCustomLabelsColor:t,onChange:Ce,colorScheme:Z})})})]})})():(()=>{const e=be(),t=!!Object.keys((null==e?void 0:e.label_colors)||{}).length;return(0,n.FD)(p.A,{gutter:16,children:[(0,n.FD)(u.A,{xs:24,md:12,children:[(0,n.Y)(f.o.Title,{level:4,style:{marginTop:"1em"},children:(0,S.t)("Access")}),(0,n.Y)(m.e,{label:(0,S.t)("Owners"),extra:(0,S.t)("Owners is a list of users who can alter the dashboard. Searchable by name or username."),children:(0,n.Y)(b.A,{allowClear:!0,ariaLabel:(0,S.t)("Owners"),disabled:K,mode:"multiple",onChange:ge,options:(e,t,i)=>ue("owners",e,t,i),value:ve()})})]}),(0,n.FD)(u.A,{xs:24,md:12,children:[(0,n.Y)(f.o.Title,{level:4,style:{marginTop:"1em"},children:(0,S.t)("Colors")}),(0,n.Y)(N,{hasCustomLabelsColor:t,onChange:Ce,colorScheme:Z})]})]})})(),(0,n.Y)(p.A,{children:(0,n.Y)(u.A,{xs:24,md:24,children:(0,n.Y)(f.o.Title,{level:4,children:(0,S.t)("Certification")})})}),(0,n.FD)(p.A,{gutter:16,children:[(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("Certified by"),name:"certifiedBy",extra:(0,S.t)("Person or group that has certified this dashboard."),children:(0,n.Y)(F.A,{type:"text",disabled:K})})}),(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{label:(0,S.t)("Certification details"),name:"certificationDetails",extra:(0,S.t)("Any additional detail to show in the certification tooltip."),children:(0,n.Y)(F.A,{type:"text",disabled:K})})})]}),(0,A.G7)(A.TO.TaggingSystem)?(0,n.Y)(p.A,{gutter:16,children:(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(f.o.Title,{level:4,css:{marginTop:"1em"},children:(0,S.t)("Tags")})})}):null,(0,A.G7)(A.TO.TaggingSystem)?(0,n.Y)(p.A,{gutter:16,children:(0,n.Y)(u.A,{xs:24,md:12,children:(0,n.Y)(m.e,{extra:(0,S.t)("A list of tags that have been applied to this chart."),children:(0,n.Y)(b.A,{ariaLabel:"Tags",mode:"multiple",value:he,options:E.m,onChange:e=>{const t=(0,$.A)(e).map((e=>({id:e.value,name:e.label})));se(t)},onClear:()=>{se([])},allowClear:!0})})})}):null,(0,n.Y)(p.A,{children:(0,n.FD)(u.A,{xs:24,md:24,children:[(0,n.Y)(f.o.Title,{level:4,style:{marginTop:"1em"},children:(0,n.FD)(g.$,{buttonStyle:"link",onClick:()=>J(!W),css:T.AH`
                  padding: 0;
                `,children:[(0,S.t)("Advanced"),W?(0,n.Y)(v.F.UpOutlined,{}):(0,n.Y)(v.F.DownOutlined,{})]})}),W&&(0,n.Y)(n.FK,{children:(0,n.Y)(m.e,{label:(0,S.t)("JSON metadata"),extra:(0,n.FD)("div",{children:[(0,S.t)("This JSON object is generated dynamically when clicking the save or overwrite button in the dashboard view. It is exposed here for reference and for power users who may want to alter specific parameters."),z&&(0,n.FD)(n.FK,{children:[" ",(0,S.t)('Please DO NOT overwrite the "filter_scopes" key.')," ",(0,n.Y)(D.A,{triggerNode:(0,n.Y)("span",{className:"alert-link",children:(0,S.t)('Use "%(menuName)s" menu instead.',{menuName:(0,S.t)("Set filter mapping")})})})]})]}),children:(0,n.Y)(H,{showLoadingForImport:!0,name:"json_metadata",value:Q,onChange:X,tabSize:2,width:"100%",height:"200px",wrapEnabled:!0})})})]})})]})})}))},76125:(e,t,i)=>{i.d(t,{A:()=>Y});var l=i(33031),r=i.n(l),n=i(2445),a=i(96540),o=i(95579),s=i(72234),c=i(17437),d=i(7148),h=i(63756),p=i(94963),u=i(50317),f=i(97470),m=i(71781),b=i(38380),g=i(23758),F=i(55556);function v(e){const{id:t,label:i,colors:l}=e,[r,o]=(0,a.useState)(!1),s=(0,a.useRef)(null),d=(0,a.useRef)(null),h=()=>l.map(((e,i)=>(0,n.Y)("span",{"data-test":"color",css:t=>c.AH`
          padding-left: ${t.sizeUnit/2}px;
          :before {
            content: '';
            display: inline-block;
            background-color: ${e};
            border: 1px solid ${"white"===e?"black":e};
            width: 9px;
            height: 10px;
          }
        `},`${t}-${i}`)));return(0,n.Y)(f.m,{"data-testid":"tooltip",overlayClassName:"color-scheme-tooltip",title:()=>(0,n.FD)(n.FK,{children:[(0,n.Y)("span",{children:i}),(0,n.Y)("div",{children:h()})]}),open:r,children:(0,n.FD)("span",{className:"color-scheme-option",onMouseEnter:()=>{const e=s.current,t=d.current;e&&t&&(e.scrollWidth>e.offsetWidth||e.scrollHeight>e.offsetHeight||t.scrollWidth>t.offsetWidth||t.scrollHeight>t.offsetHeight)&&o(!0)},onMouseLeave:()=>{o(!1)},css:c.AH`
          display: flex;
          align-items: center;
          justify-content: flex-start;
        `,"data-test":t,children:[(0,n.Y)("span",{className:"color-scheme-label",ref:s,css:e=>c.AH`
            min-width: 125px;
            padding-right: ${2*e.sizeUnit}px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
          `,children:i}),(0,n.Y)("span",{ref:d,css:e=>c.AH`
            flex: 100%;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
            padding-right: ${e.sizeUnit}px;
          `,children:h()})]})},t)}const x=(0,o.t)("The colors of this chart might be overridden by custom label colors of the related dashboard.\n    Check the JSON metadata in the Advanced settings."),C=(0,o.t)("The color scheme is determined by the related dashboard.\n        Edit the color scheme in the dashboard properties."),y=(0,o.t)("You are viewing this chart in a dashboard context with labels shared across multiple charts.\n        The color scheme selection is disabled."),S=(0,o.t)("You are viewing this chart in the context of a dashboard that is directly affecting its colors.\n        To edit the color scheme, open this chart outside of the dashboard."),w=({label:e,dashboardId:t,hasSharedLabelsColor:i,hasCustomLabelsColor:l,hasDashboardColorScheme:r})=>{const a=(0,s.DP)();if(i||l||r){const o=l&&!i?x:t&&r?C:y;return(0,n.FD)(n.FK,{children:[e," ",(0,n.Y)(f.m,{title:o,children:(0,n.Y)(b.F.WarningOutlined,{iconColor:a.colorWarning,css:c.AH`
              vertical-align: baseline;
            `,iconSize:"s"})})]})}return(0,n.Y)(n.FK,{children:e})},Y=({hasCustomLabelsColor:e=!1,hasDashboardColorScheme:t=!1,mapLabelsColors:i={},sharedLabelsColors:l=[],dashboardId:b,colorNamespace:x,chartId:C,label:y=(0,o.t)("Color scheme"),onChange:Y=()=>{},value:k,clearable:$=!1,defaultScheme:A,choices:T=[],schemes:z={},isLinear:N,...D})=>{var O;const I=l.length,E=(0,d.Ay)(),U=C&&(null==(O=E.chartsLabelsMap.get(C))?void 0:O.labels)||[],M=!!(b&&I>0&&U.some((e=>l.includes(e)))),L=b&&t,j=L||M,_=(0,s.DP)(),R=(0,a.useMemo)((()=>{if(j)return"dashboard";let e=k||A;if("SUPERSET_DEFAULT"===e){var t;const i="function"==typeof z?z():z;e=null==i||null==(t=i.SUPERSET_DEFAULT)?void 0:t.id}return e}),[A,z,j,k]),H=(0,a.useMemo)((()=>{if(j)return[{value:"dashboard",label:(0,n.Y)(f.m,{title:S,children:(0,o.t)("Dashboard scheme")})}];const e="function"==typeof z?z():z,t="function"==typeof T?T():T,i=[],l=t.filter((e=>{const t=e[0],l="SUPERSET_DEFAULT"!==t&&!i.includes(t);return i.push(t),l})).reduce(((t,[i])=>{var l;const r=e[i];let a=[];r&&(a=N?r.getColors(10):r.colors);const o={label:(0,n.Y)(v,{id:r.id,label:r.label,colors:a}),value:i};return t[null!=(l=r.group)?l:h.w.Other].options.push(o),t}),{[h.w.Custom]:{title:h.w.Custom,label:(0,o.t)("Custom color palettes"),options:[]},[h.w.Featured]:{title:h.w.Featured,label:(0,o.t)("Featured color palettes"),options:[]},[h.w.Other]:{title:h.w.Other,label:(0,o.t)("Other color palettes"),options:[]}}),a=Object.values(l).filter((e=>e.options.length>0)).map((e=>({...e,options:r()(e.options,(e=>e.label))})));return 1===a.length&&a[0].title===h.w.Other?a[0].options.map((e=>({value:e.value,label:e.customLabel||e.label}))):a.map((e=>({label:e.label,options:e.options.map((e=>({value:e.value,label:e.customLabel||e.label})))})))}),[T,L,M,N,z]);return(0,n.FD)(n.FK,{children:[(0,n.Y)(u.A,{...D,label:(0,n.Y)(w,{label:y,dashboardId:b,hasCustomLabelsColor:e,hasDashboardColorScheme:t,hasSharedLabelsColor:M})}),(0,n.Y)(m.A,{css:c.AH`
          width: 100%;
          & .ant-select-item.ant-select-item-group {
            padding-left: ${_.sizeUnit}px;
            font-size: ${_.fontSize}px;
          }
          & .ant-select-item-option-grouped {
            padding-left: ${3*_.sizeUnit}px;
          }
        `,"aria-label":(0,o.t)("Select color scheme"),allowClear:$,disabled:L||M,onChange:e=>{if(C&&(E.setOwnColorScheme(C,e),b)){const e=(0,F.Z6)(x),t=p.getNamespace(e),r=new Set(l),n=Object.keys(i).filter((e=>!r.has(e)));t.resetColorsForLabels(n)}Y(e)},placeholder:(0,o.t)("Select scheme"),value:R,showSearch:!0,getPopupContainer:e=>e.parentNode,options:H,filterOption:(e,t)=>(0,g.qY)(e,t,["label","value"],!0)})]})}},88461:(e,t,i)=>{i.d(t,{T:()=>s});var l=i(2445),r=i(72234),n=i(95579),a=i(38380),o=i(97470);function s({certifiedBy:e,details:t,size:i="l"}){const s=(0,r.DP)();return(0,l.Y)(o.m,{id:"certified-details-tooltip",title:(0,l.FD)(l.FK,{children:[e&&(0,l.Y)("div",{children:(0,l.Y)("strong",{children:(0,n.t)("Certified by %s",e)})}),(0,l.Y)("div",{children:t})]}),children:(0,l.Y)(a.F.Certified,{iconColor:s.colorPrimary,iconSize:i})})}},97567:(e,t,i)=>{i.d(t,{FA:()=>c,Ik:()=>p,dH:()=>h,iQ:()=>s,un:()=>d});var l=i(35742),r=i(58561),n=i.n(r),a=i(69088);const o=Object.freeze(["dashboard","chart","saved_query"]),s=Object.freeze({DASHBOARD:"dashboard",CHART:"chart",QUERY:"saved_query"});function c(e,t,i){l.A.get({endpoint:`/api/v1/tag/${e}`}).then((({json:e})=>t(e.result))).catch((e=>i(e)))}function d({objectType:e,objectId:t},i,r){if(void 0===e||void 0===t)throw new Error("Need to specify objectType and objectId");if(!o.includes(e))throw new Error(`objectType ${e} is invalid`);l.A.get({endpoint:`/api/v1/${e}/${t}`}).then((({json:e})=>i(e.result.tags.filter((e=>e.type===a.U.Custom))))).catch((e=>r(e)))}function h(e,t,i){const r=e.map((e=>e.name));l.A.delete({endpoint:`/api/v1/tag/?q=${n().encode(r)}`}).then((({json:e})=>e.message?t(e.message):t("Successfully Deleted Tag"))).catch((e=>{const t=e.message;return i(t||"Error Deleting Tag")}))}function p({tagIds:e=[],types:t},i,r){let n=`/api/v1/tag/get_objects/?tagIds=${e}`;t&&(n+=`&types=${t}`),l.A.get({endpoint:n}).then((({json:e})=>i(e.result))).catch((e=>r(e)))}},99813:(e,t,i)=>{i.d(t,{A:()=>be});var l=i(2445),r=i(96540),n=i(72234),a=i(53784),o=i(61225),s=i(82960),c=i(78130),d=i(72173),h=i(5556),p=i.n(h),u=i(46942),f=i.n(u),m=i(17355),b=i(15509),g=i(17437),F=i(95579),v=i(62193),x=i.n(v),C=i(81151),y=i(49588);const S=[y.B8,y.tq];function w({currentNode:e={},components:t={},filterFields:i=[],selectedChartId:l}){if(!e)return null;const{type:r}=e;if(y.oT===r&&e&&e.meta&&e.meta.chartId)return{value:e.meta.chartId,label:e.meta.sliceName||`${r} ${e.meta.chartId}`,type:r,showCheckbox:l!==e.meta.chartId,children:[]};let n=[];if(e.children&&e.children.length&&e.children.forEach((e=>{const r=w({currentNode:t[e],components:t,filterFields:i,selectedChartId:l}),a=t[e].type;S.includes(a)?n.push(r):n=n.concat(r)})),S.includes(r)){let t=null;return t=r===y.tq?(0,F.t)("All charts"):e.meta&&e.meta.text?e.meta.text:`${r} ${e.id}`,{value:e.id,label:t,type:r,children:n}}return n}function Y({components:e={},filterFields:t=[],selectedChartId:i}){return x()(e)?[]:[{...w({currentNode:e[C.wv],components:e,filterFields:t,selectedChartId:i})}]}function k(e=[],t=-1){const i=[],l=(e,r)=>{e&&e.children&&(-1===t||r<t)&&(i.push(e.value),e.children.forEach((e=>l(e,r+1))))};return e.length>0&&e.forEach((e=>{l(e,0)})),i}var $=i(12066);function A({activeFilterField:e,checkedFilterFields:t}){return(0,$.J)(e?[e]:t)}var T=i(24647);function z({activeFilterField:e,checkedFilterFields:t}){if(e)return(0,T.w)(e).chartId;if(t.length){const{chartId:e}=(0,T.w)(t[0]);return t.some((t=>(0,T.w)(t).chartId!==e))?null:e}return null}function N({checkedFilterFields:e=[],activeFilterField:t,filterScopeMap:i={},layout:l={}}){const r=A({checkedFilterFields:e,activeFilterField:t}),n=t?[t]:e,a=Y({components:l,filterFields:n,selectedChartId:z({checkedFilterFields:e,activeFilterField:t})}),o=new Set;n.forEach((e=>{(i[e].checked||[]).forEach((t=>{o.add(`${t}:${e}`)}))}));const s=[...o],c=i[r]?i[r].expanded:k(a,1);return{[r]:{nodes:a,nodesFiltered:[...a],checked:s,expanded:c}}}var D=i(47307),O=i.n(D),I=i(89143),E=i.n(I),U=i(8209),M=i.n(U),L=i(89899),j=i.n(L);function _({tabScopes:e,parentNodeValue:t,forceAggregate:i=!1,hasChartSiblings:l=!1,tabChildren:r=[],immuneChartSiblings:n=[]}){if(i||!l&&Object.entries(e).every((([e,{scope:t}])=>t&&t.length&&e===t[0]))){const i=function({tabs:e=[],tabsInScope:t=[]}){const i=[];return e.forEach((({value:e,children:l})=>{l&&!t.includes(e)&&l.forEach((({value:e,children:l})=>{l&&!t.includes(e)&&i.push(...l.filter((({type:e})=>e===y.oT)))}))})),i.map((({value:e})=>e))}({tabs:r,tabsInScope:O()(e,(({scope:e})=>e))}),l=O()(Object.values(e),(({immune:e})=>e));return{scope:[t],immune:[...new Set([...i,...l])]}}const a=Object.values(e).filter((({scope:e})=>e&&e.length));return{scope:O()(a,(({scope:e})=>e)),immune:a.length?O()(a,(({immune:e})=>e)):O()(Object.values(e),(({immune:e})=>e)).concat(n)}}function R({currentNode:e={},filterId:t,checkedChartIds:i=[]}){if(!e)return{};const{value:l,children:r}=e,n=r.filter((({type:e})=>e===y.oT)),a=r.filter((({type:e})=>e===y.B8)),o=n.filter((({value:e})=>t!==e&&!i.includes(e))).map((({value:e})=>e)),s=j()(M()((e=>e.value)),E()((e=>R({currentNode:e,filterId:t,checkedChartIds:i}))))(a);if(!x()(n)&&n.some((({value:e})=>i.includes(e)))){if(x()(a))return{scope:[l],immune:o};const{scope:e,immune:t}=_({tabScopes:s,parentNodeValue:l,forceAggregate:!0,tabChildren:a});return{scope:e,immune:o.concat(t)}}return a.length?_({tabScopes:s,parentNodeValue:l,hasChartSiblings:!x()(n),tabChildren:a,immuneChartSiblings:o}):{scope:[],immune:o}}function H({filterKey:e,nodes:t=[],checkedChartIds:i=[]}){if(t.length){const{chartId:l}=(0,T.w)(e);return R({currentNode:t[0],filterId:l,checkedChartIds:i})}return{}}var P=i(68921),B=i(4881),q=i(38491),K=i.n(q),V=i(38380);const W=(0,n.I4)(V.F.BarChartOutlined)`
  ${({theme:e})=>`\n    position: relative;\n    top: ${e.sizeUnit-1}px;\n    color: ${e.colorPrimary};\n    margin-right: ${2*e.sizeUnit}px;\n  `}
`;function J({currentNode:e={},selectedChartId:t}){if(!e)return null;const{label:i,value:r,type:n,children:a}=e;if(a&&a.length){const o=a.map((e=>J({currentNode:e,selectedChartId:t})));return{...e,label:(0,l.FD)("span",{className:f()(`filter-scope-type ${n.toLowerCase()}`,{"selected-filter":t===r}),children:[n===y.oT&&(0,l.Y)(W,{}),i]}),children:o}}return{...e,label:(0,l.Y)("span",{className:f()(`filter-scope-type ${n.toLowerCase()}`,{"selected-filter":t===r}),children:i})}}function Z({nodes:e,selectedChartId:t}){return e?e.map((e=>J({currentNode:e,selectedChartId:t}))):[]}const G={check:(0,l.Y)((()=>{const e=(0,n.DP)();return(0,l.FD)("svg",{width:"18",height:"18",viewBox:"0 0 18 18",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[(0,l.Y)("path",{d:"M16 0H2C0.89 0 0 0.9 0 2V16C0 17.1 0.89 18 2 18H16C17.11 18 18 17.1 18 16V2C18 0.9 17.11 0 16 0Z",fill:e.colorPrimary}),(0,l.Y)("path",{d:"M7 14L2 9L3.41 7.59L7 11.17L14.59 3.58L16 5L7 14Z",fill:"white"})]})}),{}),uncheck:(0,l.Y)((()=>{const e=(0,n.DP)();return(0,l.FD)("svg",{width:"18",height:"18",viewBox:"0 0 18 18",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[(0,l.Y)("path",{d:"M16 0H2C0.9 0 0 0.9 0 2V16C0 17.1 0.9 18 2 18H16C17.1 18 18 17.1 18 16V2C18 0.9 17.1 0 16 0Z",fill:e.colors.grayscale.light2}),(0,l.Y)("path",{d:"M16 2V16H2V2H16V2Z",fill:"white"})]})}),{}),halfCheck:(0,l.Y)((()=>{const e=(0,n.DP)();return(0,l.FD)("svg",{width:"18",height:"18",viewBox:"0 0 18 18",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[(0,l.Y)("path",{d:"M16 0H2C0.9 0 0 0.9 0 2V16C0 17.1 0.9 18 2 18H16C17.1 18 18 17.1 18 16V2C18 0.9 17.1 0 16 0Z",fill:e.colors.grayscale.light1}),(0,l.Y)("path",{d:"M14 10H4V8H14V10Z",fill:"white"})]})}),{}),expandClose:(0,l.Y)("span",{className:"rct-icon rct-icon-expand-close"}),expandOpen:(0,l.Y)("span",{className:"rct-icon rct-icon-expand-open"}),expandAll:(0,l.Y)("span",{className:"rct-icon rct-icon-expand-all",children:(0,F.t)("Expand all")}),collapseAll:(0,l.Y)("span",{className:"rct-icon rct-icon-collapse-all",children:(0,F.t)("Collapse all")}),parentClose:(0,l.Y)("span",{className:"rct-icon rct-icon-parent-close"}),parentOpen:(0,l.Y)("span",{className:"rct-icon rct-icon-parent-open"}),leaf:(0,l.Y)("span",{className:"rct-icon rct-icon-leaf"})},Q={nodes:p().arrayOf(B.QU).isRequired,checked:p().arrayOf(p().oneOfType([p().number,p().string])).isRequired,expanded:p().arrayOf(p().oneOfType([p().number,p().string])).isRequired,onCheck:p().func.isRequired,onExpand:p().func.isRequired,selectedChartId:p().number},X=()=>{};function ee({nodes:e=[],checked:t=[],expanded:i=[],onCheck:r,onExpand:n,selectedChartId:a}){return(0,l.Y)(K(),{showExpandAll:!0,expandOnClick:!0,showNodeIcon:!1,nodes:Z({nodes:e,selectedChartId:a}),checked:t,expanded:i,onCheck:r,onExpand:n,onClick:X,icons:G})}ee.propTypes=Q,ee.defaultProps={selectedChartId:null};var te=i(62799);const ie={label:p().string.isRequired,isSelected:p().bool.isRequired};function le({label:e,isSelected:t}){return(0,l.Y)("span",{className:f()("filter-field-item filter-container",{"is-selected":t}),children:(0,l.Y)(te.l,{htmlFor:e,children:e})})}function re({nodes:e,activeKey:t}){if(!e)return[];const i=e[0],r=i.children.map((e=>({...e,children:e.children.map((e=>{const{label:i,value:r}=e;return{...e,label:(0,l.Y)(le,{isSelected:r===t,label:i})}}))})));return[{...i,label:(0,l.Y)("span",{className:"root",children:i.label}),children:r}]}le.propTypes=ie;const ne={activeKey:p().string,nodes:p().arrayOf(B.QU).isRequired,checked:p().arrayOf(p().oneOfType([p().number,p().string])).isRequired,expanded:p().arrayOf(p().oneOfType([p().number,p().string])).isRequired,onCheck:p().func.isRequired,onExpand:p().func.isRequired,onClick:p().func.isRequired};function ae({activeKey:e,nodes:t=[],checked:i=[],expanded:r=[],onClick:n,onCheck:a,onExpand:o}){return(0,l.Y)(K(),{showExpandAll:!0,showNodeIcon:!1,expandOnClick:!0,nodes:re({nodes:t,activeKey:e}),checked:i,expanded:r,onClick:n,onCheck:a,onExpand:o,icons:G})}ae.propTypes=ne,ae.defaultProps={activeKey:null};const oe={dashboardFilters:p().objectOf(B.d2).isRequired,layout:p().object.isRequired,updateDashboardFiltersScope:p().func.isRequired,setUnsavedChanges:p().func.isRequired,onCloseModal:p().func.isRequired},se=n.I4.div`
  ${({theme:e})=>g.AH`
    display: flex;
    flex-direction: column;
    height: 80%;
    margin-right: ${-6*e.sizeUnit}px;
    font-size: ${e.fontSize}px;

    & .nav.nav-tabs {
      border: none;
    }

    & .filter-scope-body {
      flex: 1;
      max-height: calc(100% - ${32*e.sizeUnit}px);

      .filter-field-pane,
      .filter-scope-pane {
        overflow-y: auto;
      }
    }

    & .warning-message {
      padding: ${6*e.sizeUnit}px;
    }
  `}
`,ce=n.I4.div`
  ${({theme:e})=>g.AH`
    &.filter-scope-body {
      flex: 1;
      max-height: calc(100% - ${32*e.sizeUnit}px);

      .filter-field-pane,
      .filter-scope-pane {
        overflow-y: auto;
      }
    }
  `}
`,de=n.I4.div`
  ${({theme:e})=>g.AH`
    height: ${16*e.sizeUnit}px;
    border-bottom: 1px solid ${e.colorSplit};
    padding-left: ${6*e.sizeUnit}px;
    margin-left: ${-6*e.sizeUnit}px;

    h4 {
      margin-top: 0;
    }

    .selected-fields {
      margin: ${3*e.sizeUnit}px 0 ${4*e.sizeUnit}px;
      visibility: hidden;

      &.multi-edit-mode {
        visibility: visible;
      }

      .selected-scopes {
        padding-left: ${e.sizeUnit}px;
      }
    }
  `}
`,he=n.I4.div`
  ${({theme:e})=>g.AH`
    &.filters-scope-selector {
      display: flex;
      flex-direction: row;
      position: relative;
      height: 100%;

      a,
      a:active,
      a:hover {
        color: inherit;
        text-decoration: none;
      }

      .react-checkbox-tree .rct-icon.rct-icon-expand-all,
      .react-checkbox-tree .rct-icon.rct-icon-collapse-all {
        font-family: ${e.fontFamily};
        font-size: ${e.fontSize}px;
        color: ${e.colorPrimary};

        &::before {
          content: '';
        }

        &:hover {
          text-decoration: underline;
        }

        &:focus {
          outline: none;
        }
      }

      .filter-field-pane {
        position: relative;
        width: 40%;
        padding: ${4*e.sizeUnit}px;
        padding-left: 0;
        border-right: 1px solid ${e.colorBorder};

        .filter-container label {
          font-weight: ${e.fontWeightNormal};
          margin: 0 0 0 ${4*e.sizeUnit}px;
          word-break: break-all;
        }

        .filter-field-item {
          height: ${9*e.sizeUnit}px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 ${6*e.sizeUnit}px;
          margin-left: ${-6*e.sizeUnit}px;

          &.is-selected {
            border: 1px solid ${e.colorBorder};
            border-radius: ${e.borderRadius}px;
            background-color: ${e.colorBgContainer};
            margin-left: ${-6*e.sizeUnit}px;
          }
        }

        .react-checkbox-tree {
          .rct-title .root {
            font-weight: ${e.fontWeightStrong};
          }

          .rct-text {
            height: ${10*e.sizeUnit}px;
          }
        }
      }

      .filter-scope-pane {
        position: relative;
        flex: 1;
        padding: ${4*e.sizeUnit}px;
        padding-right: ${6*e.sizeUnit}px;
      }

      .react-checkbox-tree {
        flex-direction: column;
        color: ${e.colorText};
        font-size: ${e.fontSize}px;

        .filter-scope-type {
          padding: ${2*e.sizeUnit}px 0;
          display: flex;
          align-items: center;

          &.chart {
            font-weight: ${e.fontWeightNormal};
          }

          &.selected-filter {
            padding-left: ${7*e.sizeUnit}px;
            position: relative;
            color: ${e.colorBgContainerTextActive};

            &::before {
              content: ' ';
              position: absolute;
              left: 0;
              top: 50%;
              width: ${4*e.sizeUnit}px;
              height: ${4*e.sizeUnit}px;
              border-radius: ${e.borderRadius}px;
              margin-top: ${-2*e.sizeUnit}px;
              box-shadow: inset 0 0 0 2px ${e.colorBorder};
              background: ${e.colors.grayscale.light3};
            }
          }

          &.root {
            font-weight: ${e.fontWeightStrong};
          }
        }

        .rct-checkbox {
          svg {
            position: relative;
            top: 3px;
            width: ${4.5*e.sizeUnit}px;
          }
        }

        .rct-node-leaf {
          .rct-bare-label {
            &::before {
              padding-left: ${e.sizeUnit}px;
            }
          }
        }

        .rct-options {
          text-align: left;
          margin-left: 0;
          margin-bottom: ${2*e.sizeUnit}px;
        }

        .rct-text {
          margin: 0;
          display: flex;
        }

        .rct-title {
          display: block;
        }

        // disable style from react-checkbox-trees.css
        .rct-node-clickable:hover,
        .rct-node-clickable:focus,
        label:hover,
        label:active {
          background: none !important;
        }
      }

      .multi-edit-mode {
        .filter-field-item {
          padding: 0 ${4*e.sizeUnit}px 0 ${12*e.sizeUnit}px;
          margin-left: ${-12*e.sizeUnit}px;

          &.is-selected {
            margin-left: ${-13*e.sizeUnit}px;
          }
        }
      }

      .scope-search {
        position: absolute;
        right: ${4*e.sizeUnit}px;
        top: ${4*e.sizeUnit}px;
        border-radius: ${e.borderRadius}px;
        border: 1px solid ${e.colorBorder};
        padding: ${e.sizeUnit}px ${2*e.sizeUnit}px;
        font-size: ${e.fontSize}px;
        outline: none;

        &:focus {
          border: 1px solid ${e.colorPrimary};
        }
      }
    }
  `}
`,pe=n.I4.div`
  ${({theme:e})=>`\n    height: ${16*e.sizeUnit}px;\n\n    border-top: ${e.sizeUnit/4}px solid ${e.colors.primary.light3};\n    padding: ${6*e.sizeUnit}px;\n    margin: 0 0 0 ${6*-e.sizeUnit}px;\n    text-align: right;\n\n    .btn {\n      margin-right: ${4*e.sizeUnit}px;\n\n      &:last-child {\n        margin-right: 0;\n      }\n    }\n  `}
`;class ue extends r.PureComponent{constructor(e){super(e);const{dashboardFilters:t,layout:i}=e;if(Object.keys(t).length>0){const e=function({dashboardFilters:e={}}){const t=Object.values(e).map((e=>{const{chartId:t,filterName:i,columns:l,labels:r}=e,n=Object.keys(l).map((e=>({value:(0,T.s)({chartId:t,column:e}),label:r[e]||e})));return{value:t,label:i,children:n,showCheckbox:!0}}));return[{value:C.zf,type:y.tq,label:(0,F.t)("All filters"),children:t}]}({dashboardFilters:t}),l=e[0].children;this.allfilterFields=[],l.forEach((({children:e})=>{e.forEach((e=>{this.allfilterFields.push(e.value)}))})),this.defaultFilterKey=l[0].children[0].value;const r=Object.values(t).reduce(((e,{chartId:l,columns:r})=>({...e,...Object.keys(r).reduce(((e,r)=>{const n=(0,T.s)({chartId:l,column:r}),a=Y({components:i,filterFields:[n],selectedChartId:l}),o=k(a,1),s=((0,P._i)({filterScope:t[l].scopes[r]})||[]).filter((e=>e!==l));return{...e,[n]:{nodes:a,nodesFiltered:[...a],checked:s,expanded:o}}}),{})})),{}),{chartId:n}=(0,T.w)(this.defaultFilterKey),a=[],o=this.defaultFilterKey,s=[C.zf].concat(n),c=N({checkedFilterFields:a,activeFilterField:o,filterScopeMap:r,layout:i});this.state={showSelector:!0,activeFilterField:o,searchText:"",filterScopeMap:{...r,...c},filterFieldNodes:e,checkedFilterFields:a,expandedFilterIds:s}}else this.state={showSelector:!1};this.filterNodes=this.filterNodes.bind(this),this.onChangeFilterField=this.onChangeFilterField.bind(this),this.onCheckFilterScope=this.onCheckFilterScope.bind(this),this.onExpandFilterScope=this.onExpandFilterScope.bind(this),this.onSearchInputChange=this.onSearchInputChange.bind(this),this.onCheckFilterField=this.onCheckFilterField.bind(this),this.onExpandFilterField=this.onExpandFilterField.bind(this),this.onClose=this.onClose.bind(this),this.onSave=this.onSave.bind(this)}onCheckFilterScope(e=[]){const{activeFilterField:t,filterScopeMap:i,checkedFilterFields:l}=this.state,r=A({activeFilterField:t,checkedFilterFields:l}),n=t?[t]:l,a={...i[r],checked:e},o=function({checked:e=[],filterFields:t=[],filterScopeMap:i={}}){const l=e.reduce(((e,t)=>{const[i,l]=t.split(":");return{...e,[l]:(e[l]||[]).concat(parseInt(i,10))}}),{});return t.reduce(((e,t)=>({...e,[t]:{...i[t],checked:l[t]||[]}})),{})}({checked:e,filterFields:n,filterScopeMap:i});this.setState((()=>({filterScopeMap:{...i,...o,[r]:a}})))}onExpandFilterScope(e=[]){const{activeFilterField:t,checkedFilterFields:i,filterScopeMap:l}=this.state,r=A({activeFilterField:t,checkedFilterFields:i}),n={...l[r],expanded:e};this.setState((()=>({filterScopeMap:{...l,[r]:n}})))}onCheckFilterField(e=[]){const{layout:t}=this.props,{filterScopeMap:i}=this.state,l=N({checkedFilterFields:e,activeFilterField:null,filterScopeMap:i,layout:t});this.setState((()=>({activeFilterField:null,checkedFilterFields:e,filterScopeMap:{...i,...l}})))}onExpandFilterField(e=[]){this.setState((()=>({expandedFilterIds:e})))}onChangeFilterField(e={}){const{layout:t}=this.props,i=e.value,{activeFilterField:l,checkedFilterFields:r,filterScopeMap:n}=this.state;if(i===l){const e=N({checkedFilterFields:r,activeFilterField:null,filterScopeMap:n,layout:t});this.setState({activeFilterField:null,filterScopeMap:{...n,...e}})}else if(this.allfilterFields.includes(i)){const e=N({checkedFilterFields:r,activeFilterField:i,filterScopeMap:n,layout:t});this.setState({activeFilterField:i,filterScopeMap:{...n,...e}})}}onSearchInputChange(e){this.setState({searchText:e.target.value},this.filterTree)}onClose(){this.props.onCloseModal()}onSave(){const{filterScopeMap:e}=this.state,t=this.allfilterFields.reduce(((t,i)=>{const{nodes:l}=e[i],r=e[i].checked;return{...t,[i]:H({filterKey:i,nodes:l,checkedChartIds:r})}}),{});this.props.updateDashboardFiltersScope(t),this.props.setUnsavedChanges(!0),this.props.onCloseModal()}filterTree(){if(this.state.searchText){const e=e=>{const{activeFilterField:t,checkedFilterFields:i,filterScopeMap:l}=e,r=A({activeFilterField:t,checkedFilterFields:i}),n=l[r].nodes.reduce(this.filterNodes,[]),a=k([...n]),o={...l[r],nodesFiltered:n,expanded:a};return{filterScopeMap:{...l,[r]:o}}};this.setState(e)}else this.setState((e=>{const{activeFilterField:t,checkedFilterFields:i,filterScopeMap:l}=e,r=A({activeFilterField:t,checkedFilterFields:i}),n={...l[r],nodesFiltered:l[r].nodes};return{filterScopeMap:{...l,[r]:n}}}))}filterNodes(e=[],t={}){const{searchText:i}=this.state,l=(t.children||[]).reduce(this.filterNodes,[]);return(t.label.toLocaleLowerCase().indexOf(i.toLocaleLowerCase())>-1||l.length)&&e.push({...t,children:l}),e}renderFilterFieldList(){const{activeFilterField:e,filterFieldNodes:t,checkedFilterFields:i,expandedFilterIds:r}=this.state;return(0,l.Y)(ae,{activeKey:e,nodes:t,checked:i,expanded:r,onClick:this.onChangeFilterField,onCheck:this.onCheckFilterField,onExpand:this.onExpandFilterField})}renderFilterScopeTree(){const{filterScopeMap:e,activeFilterField:t,checkedFilterFields:i,searchText:r}=this.state,n=A({activeFilterField:t,checkedFilterFields:i}),a=z({activeFilterField:t,checkedFilterFields:i});return(0,l.FD)(l.FK,{children:[(0,l.Y)(m.A,{className:"filter-text scope-search multi-edit-mode",placeholder:(0,F.t)("Search..."),type:"text",value:r,onChange:this.onSearchInputChange}),(0,l.Y)(ee,{nodes:e[n].nodesFiltered,checked:e[n].checked,expanded:e[n].expanded,onCheck:this.onCheckFilterScope,onExpand:this.onExpandFilterScope,selectedChartId:a})]})}renderEditingFiltersName(){const{dashboardFilters:e}=this.props,{activeFilterField:t,checkedFilterFields:i}=this.state,r=[].concat(t||i).map((t=>{const{chartId:i,column:l}=(0,T.w)(t);return e[i].labels[l]||l}));return(0,l.FD)("div",{className:"selected-fields multi-edit-mode",children:[0===r.length&&(0,F.t)("No filter is selected."),1===r.length&&(0,F.t)("Editing 1 filter:"),r.length>1&&(0,F.t)("Batch editing %d filters:",r.length),(0,l.Y)("span",{className:"selected-scopes",children:r.join(", ")})]})}render(){const{showSelector:e}=this.state;return(0,l.FD)(se,{children:[(0,l.FD)(de,{children:[(0,l.Y)("h4",{children:(0,F.t)("Configure filter scopes")}),e&&this.renderEditingFiltersName()]}),(0,l.Y)(ce,{className:"filter-scope-body",children:e?(0,l.FD)(he,{className:"filters-scope-selector",children:[(0,l.Y)("div",{className:f()("filter-field-pane multi-edit-mode"),children:this.renderFilterFieldList()}),(0,l.Y)("div",{className:"filter-scope-pane multi-edit-mode",children:this.renderFilterScopeTree()})]}):(0,l.Y)("div",{className:"warning-message",children:(0,F.t)("There are no filters in this dashboard.")})}),(0,l.FD)(pe,{children:[(0,l.Y)(b.$,{buttonSize:"small",onClick:this.onClose,children:(0,F.t)("Close")}),e&&(0,l.Y)(b.$,{buttonSize:"small",buttonStyle:"primary",onClick:this.onSave,children:(0,F.t)("Save")})]})]})}}ue.propTypes=oe;const fe=(0,o.Ng)((function({dashboardLayout:e,dashboardFilters:t}){return{dashboardFilters:t,layout:e.present}}),(function(e){return(0,s.zH)({updateDashboardFiltersScope:c.B8,setUnsavedChanges:d.MR},e)}))(ue),me=n.I4.div((({theme:{sizeUnit:e}})=>({padding:2*e,paddingBottom:3*e})));class be extends r.PureComponent{constructor(e){super(e),this.modal=void 0,this.modal=(0,r.createRef)(),this.handleCloseModal=this.handleCloseModal.bind(this)}handleCloseModal(){var e;null==this||null==(e=this.modal)||null==(e=e.current)||null==e.close||e.close()}render(){const e={onCloseModal:this.handleCloseModal};return(0,l.Y)(a.g,{ref:this.modal,triggerNode:this.props.triggerNode,modalBody:(0,l.Y)(me,{children:(0,l.Y)(fe,{...e})}),width:"80%"})}}}}]);