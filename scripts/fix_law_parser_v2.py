#!/usr/bin/env python3
from pathlib import Path
import re

P=Path('index.html')
s=P.read_text(encoding='utf-8')
MARK='PMAL_LAW_REF_V2'
if MARK in s:
    print('parser legal v2 já aplicado')
    raise SystemExit(0)

def replace_function(src,name,new_block):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m: raise SystemExit(f'função {name} não encontrada')
    start=m.start(); brace=src.find('{',m.start()); depth=0; quote=None; esc=False; end=None
    for i in range(brace,len(src)):
        ch=src[i]
        if quote:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==quote:quote=None
            continue
        if ch in ('"',"'",'`'):quote=ch;continue
        if ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:end=i+1;break
    if not end: raise SystemExit(f'fim da função {name} não encontrado')
    return src[:start]+new_block+src[end:]

NEW_PARSE=r'''/* PMAL_LAW_REF_V2 — parser multi-referência por cláusula; evita cruzar artigo de um diploma com outro */
function parseRefs(f){
  if(!f)return [];
  const refs=[],seen={};
  function normArtToken(v){
    v=String(v||'').trim().replace(/\s+/g,'').replace(/[‐‑–—]/g,'-').replace(/\./g,'').replace(/[º°]/g,'');
    v=v.replace(/^(\d+)[oO]$/,'$1');
    let m=v.match(/^(\d+)(?:-?([A-Fa-f]))?$/);
    return m?(m[1]+(m[2]?m[2].toUpperCase():'')):'';
  }
  function addRef(tok,art){
    art=normArtToken(art);
    let key=art?(tok.dipl+' '+art):tok.base;
    if(tok.dipl==='Lei5346')key=art?('Lei5346 '+art):'Lei 5.346';
    if(!key||seen[key])return;
    seen[key]=1;
    let nome=tok.nome||tok.dipl;
    refs.push({key:key,label:art?('art. '+art+' de '+nome):nome,dipl:tok.dipl,art:art,baseKey:tok.base});
  }
  const specs=[
    {pat:'(?:Lei\\s*(?:n[ºo°.]*)?\\s*)?5\\.?346(?:\\/\\d{2,4})?',dipl:'Lei5346',base:'Lei 5.346',nome:'Lei 5.346/92 (Estatuto PM/AL)'},
    {pat:'(?:CADH|Pacto de S[ãa]o Jos[ée]|Conven[çc][ãa]o Americana)',dipl:'CADH',base:'CADH',nome:'CADH'},
    {pat:'(?:Decreto\\s*)?37\\.?042(?:\\/\\d{2,4})?',dipl:'RD',base:'RD',nome:'Regulamento Disciplinar PM/AL'},
    {pat:'(?:Lei\\s*)?14\\.?751(?:\\/\\d{2,4})?',dipl:'LO',base:'LO',nome:'Lei 14.751/2023'},
    {pat:'(?:Lei\\s*)?14\\.?133(?:\\/\\d{2,4})?',dipl:'L14133',base:'L14133',nome:'Lei 14.133/2021'},
    {pat:'(?:Lei\\s*)?11\\.?343(?:\\/\\d{2,4})?',dipl:'L11343',base:'L11343',nome:'Lei 11.343/2006'},
    {pat:'(?:(?:Lei\\s*)?8\\.?069(?:\\/\\d{2,4})?|\\bECA\\b)',dipl:'L8069',base:'L8069',nome:'ECA'},
    {pat:'(?:(?:Lei\\s*)?8\\.?072(?:\\/\\d{2,4})?|11\\.?464)',dipl:'L8072',base:'L8072',nome:'Lei 8.072/1990'},
    {pat:'(?:Lei\\s*)?13\\.?869(?:\\/\\d{2,4})?',dipl:'L13869',base:'L13869',nome:'Lei 13.869/2019'},
    {pat:'(?:(?:Lei\\s*)?11\\.?340(?:\\/\\d{2,4})?|\\bLMP\\b|Lei Maria da Penha)',dipl:'L11340',base:'L11340',nome:'Lei Maria da Penha'},
    {pat:'(?:Lei\\s*)?10\\.?826(?:\\/\\d{2,4})?',dipl:'L10826',base:'L10826',nome:'Lei 10.826/2003'},
    {pat:'(?:(?:Lei\\s*)?9\\.?503(?:\\/\\d{2,4})?|\\bCTB\\b)',dipl:'L9503',base:'L9503',nome:'CTB'},
    {pat:'(?:Lei\\s*)?12\\.?850(?:\\/\\d{2,4})?',dipl:'L12850',base:'L12850',nome:'Lei 12.850/2013'},
    {pat:'(?:Lei\\s*)?9\\.?455(?:\\/\\d{2,4})?',dipl:'L9455',base:'L9455',nome:'Lei 9.455/1997'},
    {pat:'(?:Lei\\s*)?7\\.?716(?:\\/\\d{2,4})?',dipl:'L7716',base:'L7716',nome:'Lei 7.716/1989'},
    {pat:'(?:Lei\\s*)?9\\.?605(?:\\/\\d{2,4})?',dipl:'L9605',base:'L9605',nome:'Lei 9.605/1998'},
    {pat:'(?:Lei\\s*)?7\\.?960(?:\\/\\d{2,4})?',dipl:'L7960',base:'L7960',nome:'Lei 7.960/1989'},
    {pat:'(?:(?:Lei\\s*)?9\\.?099(?:\\/\\d{2,4})?|\\bJECRIM\\b)',dipl:'L9099',base:'L9099',nome:'Lei 9.099/1995'},
    {pat:'(?:(?:Lei\\s*)?10\\.?259(?:\\/\\d{2,4})?|\\bJEF\\b)',dipl:'L10259',base:'L10259',nome:'Lei 10.259/2001'},
    {pat:'(?:(?:Lei\\s*)?8\\.?429(?:\\/\\d{2,4})?|14\\.?230)',dipl:'L8429',base:'L8429',nome:'Lei 8.429/1992'},
    {pat:'(?:Lei\\s*)?8\\.?987(?:\\/\\d{2,4})?',dipl:'L8987',base:'L8987',nome:'Lei 8.987/1995'},
    {pat:'(?:Lei\\s*)?9\\.?784(?:\\/\\d{2,4})?',dipl:'L9784',base:'L9784',nome:'Lei 9.784/1999'},
    {pat:'(?:Lei\\s*)?8\\.?112(?:\\/\\d{2,4})?',dipl:'L8112',base:'L8112',nome:'Lei 8.112/1990'},
    {pat:'(?:Lei\\s*)?4\\.?717(?:\\/\\d{2,4})?',dipl:'L4717',base:'L4717',nome:'Lei 4.717/1965'},
    {pat:'(?:Lei\\s*)?13\\.?300(?:\\/\\d{2,4})?',dipl:'L13300',base:'L13300',nome:'Lei 13.300/2016'},
    {pat:'(?:(?:Lei\\s*)?7\\.?210(?:\\/\\d{2,4})?|\\bLEP\\b)',dipl:'LEP',base:'LEP',nome:'LEP'},
    {pat:'(?:Lei\\s*)?12\\.?016(?:\\/\\d{2,4})?',dipl:'L12016',base:'L12016',nome:'Lei 12.016/2009'},
    {pat:'(?:Lei\\s*)?9\\.?474(?:\\/\\d{2,4})?',dipl:'L9474',base:'L9474',nome:'Lei 9.474/1997'},
    {pat:'(?:Lei\\s*)?12\\.?830(?:\\/\\d{2,4})?',dipl:'L12830',base:'L12830',nome:'Lei 12.830/2013'},
    {pat:'(?:Lei\\s*)?12\\.?037(?:\\/\\d{2,4})?',dipl:'L12037',base:'L12037',nome:'Lei 12.037/2009'},
    {pat:'(?:Lei\\s*)?9\\.?507(?:\\/\\d{2,4})?',dipl:'L9507',base:'L9507',nome:'Lei 9.507/1997'},
    {pat:'(?:Lei\\s*)?9\\.?296(?:\\/\\d{2,4})?',dipl:'L9296',base:'L9296',nome:'Lei 9.296/1996'}
  ];
  let text=String(f).replace(/\.\s+(?=(?:Lei|CF(?:\/88)?|CPPM|CPP|CPM|CP|CADH|ECA|CTB|LMP|LEP|JECRIM|JEF|Decreto)\b)/gi,'; ');
  let clauses=text.split(';');
  clauses.forEach(function(clause){
    if(!clause.trim())return;
    let toks=[];
    specs.forEach(function(sp){
      let re=new RegExp(sp.pat,'gi'),m;
      while((m=re.exec(clause))!==null){toks.push({start:m.index,end:re.lastIndex,dipl:sp.dipl,base:sp.base,nome:sp.nome,special:true,used:false});if(m[0].length===0)re.lastIndex++;}
    });
    let cr=/\b(CPPM|CPP|CPM|CP|CF)(?:\/88)?\b/gi,cm;
    while((cm=cr.exec(clause))!==null){let d=cm[1].toUpperCase();toks.push({start:cm.index,end:cr.lastIndex,dipl:d,base:d,nome:(DIPL_NOME[d]||d),special:false,used:false});}
    toks.sort(function(a,b){return a.start-b.start;});
    let arts=[],ar=/\b[Aa]rts?\.?\s*([^:;]{1,60})/g,am;
    while((am=ar.exec(clause))!==null){
      let seg=am[1];
      seg=seg.split('§')[0].split(/\.\s/)[0];
      let cut=seg.search(/\b(?:Lei|CF(?:\/88)?|CPPM|CPP|CPM|CP|CADH|ECA|CTB|LMP|LEP|JECRIM|JEF|Decreto)\b/i);
      if(cut>=0)seg=seg.slice(0,cut);
      let nums=[],nr=/\d+[A-Fa-f]\b|\d+(?:\s*\.?\s*[º°oO]\.?)?(?:\s*[-‐‑–—]\s*[A-Fa-f])?/g,nm;
      while((nm=nr.exec(seg))!==null){let a=normArtToken(nm[0]);if(a&&nums.indexOf(a)<0)nums.push(a);}
      if(nums.length)arts.push({start:am.index,nums:nums});
    }
    arts.forEach(function(a){
      if(!toks.length)return;
      let best=null,dist=Infinity;
      toks.forEach(function(t){let c=(t.start+t.end)/2,d=Math.abs(a.start-c);if(d<dist){dist=d;best=t;}});
      if(best){best.used=true;a.nums.forEach(function(n){addRef(best,n);});}
    });
    toks.forEach(function(t){if(t.special&&!t.used)addRef(t,'');});
  });
  return refs;
}
function parseRef(f){var r=parseRefs(f);return r.length?r[0]:null;}'''

NEW_BUILD=r'''function buildKeyToQids(){
  if(KEY_TO_QIDS)return KEY_TO_QIDS;
  KEY_TO_QIDS={};
  QQ.forEach(function(q){
    parseRefs(q.f).forEach(function(r){
      var key=DISP[r.key]?r.key:((r.baseKey&&DISP[r.baseKey])?r.baseKey:null);
      if(!key)return;
      if(!KEY_TO_QIDS[key])KEY_TO_QIDS[key]=[];
      if(KEY_TO_QIDS[key].indexOf(q.id)<0)KEY_TO_QIDS[key].push(q.id);
    });
  });
  return KEY_TO_QIDS;
}'''

s=replace_function(s,'parseRef',NEW_PARSE)
s=replace_function(s,'buildKeyToQids',NEW_BUILD)
P.write_text(s,encoding='utf-8')
print('parser legal v2 aplicado: referências por cláusula + múltiplos artigos/diplomas')
