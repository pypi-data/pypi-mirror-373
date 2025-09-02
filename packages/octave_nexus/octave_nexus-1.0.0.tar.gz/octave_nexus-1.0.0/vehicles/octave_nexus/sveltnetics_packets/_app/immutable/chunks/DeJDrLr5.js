import{t as s,s as c,e as u}from"./CCqubVTp.js";const m=async({net_path:n,address:t})=>{const e=await new s(new c({fullnode:n,network:u.CUSTOM})).view({payload:{function:"0x1::account::get_sequence_number",typeArguments:[],functionArguments:[t]}}),o=e[0];return{proceeds:e,sequence_number:o}};export{m as a};
//# sourceMappingURL=DeJDrLr5.js.map
