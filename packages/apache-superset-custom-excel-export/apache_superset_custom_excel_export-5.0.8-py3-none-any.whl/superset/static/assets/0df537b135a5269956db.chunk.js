"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[6830],{41734:(e,t,s)=>{s.r(t),s.d(t,{UserInfo:()=>x,default:()=>P});var a=s(2445),i=s(96540),n=s(72234),r=s(17437),o=s(35742),l=s(95579),d=s(51713),c=s(5261),u=s(55957),m=s(56268),h=s(17355),p=s(79633);function f({show:e,onHide:t,onSave:s,isEditMode:i,user:n}){const{addDangerToast:r,addSuccessToast:d}=(0,c.Yf)(),u=i?["first_name","last_name"]:["password","confirm_password"],f=i?{first_name:null==n?void 0:n.firstName,last_name:null==n?void 0:n.lastName}:{};return(0,a.Y)(p.k,{show:e,onHide:t,title:i?(0,l.t)("Edit user"):(0,l.t)("Reset password"),onSave:s,formSubmitHandler:async e=>{try{const{confirm_password:t,...a}=e;await o.A.put({endpoint:"/api/v1/me/",jsonPayload:{...a}}),d(i?(0,l.t)("The user was updated successfully"):(0,l.t)("The password reset was successful")),s()}catch(e){r((0,l.t)("Something went wrong while saving the user info"))}},requiredFields:u,initialValues:f,children:i?(0,a.Y)((()=>(0,a.FD)(a.FK,{children:[(0,a.Y)(m.e,{name:"first_name",label:(0,l.t)("First name"),rules:[{required:!0,message:(0,l.t)("First name is required")}],children:(0,a.Y)(h.A,{name:"first_name",placeholder:(0,l.t)("Enter the user's first name")})}),(0,a.Y)(m.e,{name:"last_name",label:(0,l.t)("Last name"),rules:[{required:!0,message:(0,l.t)("Last name is required")}],children:(0,a.Y)(h.A,{name:"last_name",placeholder:(0,l.t)("Enter the user's last name")})})]})),{}):(0,a.Y)((()=>(0,a.FD)(a.FK,{children:[(0,a.Y)(m.e,{name:"password",label:(0,l.t)("Password"),rules:[{required:!0,message:(0,l.t)("Password is required")}],children:(0,a.Y)(h.A.Password,{name:"password",placeholder:"Enter the user's password"})}),(0,a.Y)(m.e,{name:"confirm_password",label:(0,l.t)("Confirm Password"),dependencies:["password"],rules:[{required:!0,message:(0,l.t)("Please confirm your password")},({getFieldValue:e})=>({validator:(t,s)=>s&&e("password")!==s?Promise.reject(new Error((0,l.t)("Passwords do not match!"))):Promise.resolve()})],children:(0,a.Y)(h.A.Password,{name:"confirm_password",placeholder:(0,l.t)("Confirm the user's password")})})]})),{})})}const w=e=>(0,a.Y)(f,{...e,isEditMode:!1}),g=e=>(0,a.Y)(f,{...e,isEditMode:!0});var b=s(38380),Y=s(62683);const y=n.I4.div`
  ${({theme:e})=>r.AH`
    font-weight: ${e.fontWeightStrong};
    text-align: left;
    font-size: 18px;
    padding: ${3*e.sizeUnit}px;
    padding-left: ${7*e.sizeUnit}px;
    display: inline-block;
    line-height: ${9*e.sizeUnit}px;
    width: 100%;
    background-color: ${e.colors.grayscale.light5};
    margin-bottom: ${6*e.sizeUnit}px;
  `}
`,F=n.I4.div`
  ${({theme:e})=>r.AH`
    margin: 0px ${3*e.sizeUnit}px ${6*e.sizeUnit}px
      ${3*e.sizeUnit}px;
    background-color: ${e.colors.grayscale.light5};
  `}
`,v=n.I4.div`
  ${({theme:e})=>r.AH`
    .ant-row {
      margin: 0px ${3*e.sizeUnit}px ${6*e.sizeUnit}px
        ${3*e.sizeUnit}px;
    }
    && .menu > .ant-menu {
      padding: 0px;
    }
    && .nav-right {
      left: 0;
      padding-left: ${4*e.sizeUnit}px;
      position: relative;
      height: ${15*e.sizeUnit}px;
    }
  `}
`,S=n.I4.span`
  font-weight: ${({theme:e})=>e.fontWeightStrong};
`;var A;function x({user:e}){const t=(0,n.DP)(),[s,m]=(0,i.useState)({resetPassword:!1,edit:!1}),h=e=>m((t=>({...t,[e]:!0}))),p=e=>m((t=>({...t,[e]:!1}))),{addDangerToast:f}=(0,c.Yf)(),[x,P]=(0,i.useState)(e);(0,i.useEffect)((()=>{$()}),[]);const $=(0,i.useCallback)((()=>{o.A.get({endpoint:"/api/v1/me/"}).then((({json:e})=>{const t={...e.result,firstName:e.result.first_name,lastName:e.result.last_name};P(t)})).catch((e=>{f("Failed to fetch user info:",e)}))}),[x]),k=[{name:(0,a.FD)(a.FK,{children:[(0,a.Y)(b.F.LockOutlined,{iconColor:t.colorPrimary,iconSize:"m",css:r.AH`
              margin: auto ${2*t.sizeUnit}px auto 0;
              vertical-align: text-top;
            `}),(0,l.t)("Reset my password")]}),buttonStyle:"secondary",onClick:()=>{h(A.ResetPassword)},"data-test":"reset-password-button"},{name:(0,a.FD)(a.FK,{children:[(0,a.Y)(b.F.FormOutlined,{iconSize:"m",css:r.AH`
              margin: auto ${2*t.sizeUnit}px auto 0;
              vertical-align: text-top;
            `}),(0,l.t)("Edit user")]}),buttonStyle:"primary",onClick:()=>{h(A.Edit)},"data-test":"edit-user-button"}];return(0,a.FD)(v,{children:[(0,a.Y)(y,{children:"Your user information"}),(0,a.Y)(F,{children:(0,a.FD)(Y.S,{defaultActiveKey:["userInfo","personalInfo"],ghost:!0,children:[(0,a.Y)(Y.S.Panel,{header:(0,a.Y)(S,{children:"User info"}),children:(0,a.FD)(u.A,{bordered:!0,size:"small",column:1,labelStyle:{width:"120px"},children:[(0,a.Y)(u.A.Item,{label:"User Name",children:e.username}),(0,a.Y)(u.A.Item,{label:"Is Active?",children:e.isActive?"Yes":"No"}),(0,a.Y)(u.A.Item,{label:"Role",children:e.roles?Object.keys(e.roles).join(", "):"None"}),(0,a.Y)(u.A.Item,{label:"Login count",children:e.loginCount})]})},"userInfo"),(0,a.Y)(Y.S.Panel,{header:(0,a.Y)(S,{children:"Personal info"}),children:(0,a.FD)(u.A,{bordered:!0,size:"small",column:1,labelStyle:{width:"120px"},children:[(0,a.Y)(u.A.Item,{label:"First Name",children:x.firstName}),(0,a.Y)(u.A.Item,{label:"Last Name",children:x.lastName}),(0,a.Y)(u.A.Item,{label:"Email",children:e.email})]})},"personalInfo")]})}),s.resetPassword&&(0,a.Y)(w,{onHide:()=>p(A.ResetPassword),show:s.resetPassword,onSave:()=>{p(A.ResetPassword)}}),s.edit&&(0,a.Y)(g,{onHide:()=>p(A.Edit),show:s.edit,onSave:()=>{p(A.Edit),$()},user:x}),(0,a.Y)(d.A,{buttons:k})]})}!function(e){e.ResetPassword="resetPassword",e.Edit="edit"}(A||(A={}));const P=x},79633:(e,t,s)=>{s.d(t,{k:()=>d});var a=s(2445),i=s(96540),n=s(95579),r=s(15509),o=s(29221),l=s(84335);function d({show:e,onHide:t,title:s,onSave:d,children:c,initialValues:u={},formSubmitHandler:m,bodyStyle:h={},requiredFields:p=[],name:f}){const[w]=o.l.useForm(),[g,b]=(0,i.useState)(!1),Y=(0,i.useCallback)((()=>{w.resetFields(),b(!1)}),[w]),[y,F]=(0,i.useState)(!0),v=(0,i.useCallback)((()=>{Y(),t()}),[t,Y]),S=(0,i.useCallback)((()=>{Y(),d()}),[d,Y]),A=(0,i.useCallback)((async e=>{try{b(!0),await m(e),S()}catch(e){console.error(e)}finally{b(!1)}}),[m,S]),x=()=>{const e=w.getFieldsError().some((({errors:e})=>e.length)),t=w.getFieldsValue(),s=p.some((e=>!t[e]));F(e||s)};return(0,a.Y)(l.aF,{name:f,show:e,title:s,onHide:v,bodyStyle:h,footer:(0,a.FD)(a.FK,{children:[(0,a.Y)(r.$,{buttonStyle:"secondary","data-test":"modal-cancel-button",onClick:v,children:(0,n.t)("Cancel")}),(0,a.Y)(r.$,{buttonStyle:"primary",htmlType:"submit",onClick:()=>w.submit(),"data-test":"form-modal-save-button",disabled:g||y,children:g?(0,n.t)("Saving..."):(0,n.t)("Save")})]}),children:(0,a.Y)(o.l,{form:w,layout:"vertical",onFinish:A,initialValues:u,onValuesChange:x,onFieldsChange:x,children:"function"==typeof c?c(w):c})})}}}]);