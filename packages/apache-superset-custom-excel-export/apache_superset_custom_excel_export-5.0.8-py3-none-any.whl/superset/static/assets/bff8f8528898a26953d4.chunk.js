(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[7094],{19049:(e,t,r)=>{var i=r(79920)("capitalize",r(14792),r(96493));i.placeholder=r(2874),e.exports=i},33117:(e,t,r)=>{"use strict";r.r(t),r.d(t,{default:()=>w});var i,n=r(19049),l=r.n(n),a=r(2445),o=r(72234),s=r(17437),c=r(35742),u=r(95579),d=r(30983),h=r(64658),m=r(29221),p=r(38380),g=r(91996),f=r(15509),A=r(17355),y=r(96540),Y=r(38708);!function(e){e[e.AuthOID=0]="AuthOID",e[e.AuthDB=1]="AuthDB",e[e.AuthLDAP=2]="AuthLDAP",e[e.AuthOauth=4]="AuthOauth"}(i||(i={}));const b=(0,o.I4)(d.Z)`
  ${({theme:e})=>s.AH`
    max-width: 400px;
    width: 100%;
    margin-top: ${e.marginXL}px;
    color: ${e.colorBgContainer};
    background: ${e.colorBgBase};
    .ant-form-item-label label {
      color: ${e.colorPrimary};
    }
  `}
`,D=(0,o.I4)(h.o.Text)`
  ${({theme:e})=>s.AH`
    font-size: ${e.fontSizeSM}px;
  `}
`;function w(){const[e]=m.l.useForm(),[t,r]=(0,y.useState)(!1),n=(0,Y.Ay)(),o=n.common.conf.AUTH_TYPE,d=n.common.conf.AUTH_PROVIDERS,w=n.common.conf.AUTH_USER_REGISTRATION,$=e=>{if(!e||"string"!=typeof e)return;const t=`${l()(e)}Outlined`,r=p.F[t];return r&&"function"==typeof r?(0,a.Y)(r,{}):void 0};return(0,a.Y)(g.s,{justify:"center",align:"center","data-test":"login-form",css:s.AH`
        width: 100%;
        height: calc(100vh - 200px);
      `,children:(0,a.FD)(b,{title:(0,u.t)("Sign in"),padded:!0,children:[o===i.AuthOID&&(0,a.Y)(g.s,{justify:"center",vertical:!0,gap:"middle",children:(0,a.Y)(m.l,{layout:"vertical",requiredMark:"optional",form:e,children:d.map((e=>(0,a.Y)(m.l.Item,{children:(0,a.FD)(f.$,{href:`/login/${e.name}`,block:!0,iconPosition:"start",icon:$(e.name),children:[(0,u.t)("Sign in with")," ",l()(e.name)]})})))})}),o===i.AuthOauth&&(0,a.Y)(g.s,{justify:"center",gap:0,vertical:!0,children:(0,a.Y)(m.l,{layout:"vertical",requiredMark:"optional",form:e,children:d.map((e=>(0,a.Y)(m.l.Item,{children:(0,a.FD)(f.$,{href:`/login/${e.name}`,block:!0,iconPosition:"start",icon:$(e.name),children:[(0,u.t)("Sign in with")," ",l()(e.name)]})})))})}),(o===i.AuthDB||o===i.AuthLDAP)&&(0,a.FD)(g.s,{justify:"center",vertical:!0,gap:"middle",children:[(0,a.Y)(h.o.Text,{type:"secondary",children:(0,u.t)("Enter your login and password below:")}),(0,a.FD)(m.l,{layout:"vertical",requiredMark:"optional",form:e,onFinish:e=>{r(!0),c.A.postForm("/login/",e,"").finally((()=>{r(!1)}))},children:[(0,a.Y)(m.l.Item,{label:(0,a.Y)(D,{children:(0,u.t)("Username:")}),name:"username",rules:[{required:!0,message:(0,u.t)("Please enter your username")}],children:(0,a.Y)(A.A,{autoFocus:!0,prefix:(0,a.Y)(p.F.UserOutlined,{iconSize:"l"}),"data-test":"username-input"})}),(0,a.Y)(m.l.Item,{label:(0,a.Y)(D,{children:(0,u.t)("Password:")}),name:"password",rules:[{required:!0,message:(0,u.t)("Please enter your password")}],children:(0,a.Y)(A.A.Password,{prefix:(0,a.Y)(p.F.KeyOutlined,{iconSize:"l"}),"data-test":"password-input"})}),(0,a.Y)(m.l.Item,{label:null,children:(0,a.FD)(g.s,{css:s.AH`
                    width: 100%;
                  `,children:[(0,a.Y)(f.$,{block:!0,type:"primary",htmlType:"submit",loading:t,"data-test":"login-button",children:(0,u.t)("Sign in")}),w&&(0,a.Y)(f.$,{block:!0,type:"default",href:"/register/","data-test":"register-button",children:(0,u.t)("Register")})]})})]})]})]})})}},96493:e=>{e.exports={cap:!1,curry:!1,fixed:!1,immutable:!1,rearg:!1}}}]);