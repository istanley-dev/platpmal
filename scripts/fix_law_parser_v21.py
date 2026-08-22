#!/usr/bin/env python3
from pathlib import Path

P=Path('index.html')
s=P.read_text(encoding='utf-8')
MARK='PMAL_LAW_REF_V21'
if MARK in s:
    print('parser legal v2.1 já aplicado')
    raise SystemExit(0)

start=s.find("    let arts=[],ar=/\\b[Aa]rts?")
if start<0:
    raise SystemExit('bloco de extração de artigos do parser v2 não encontrado')
end=s.find('    arts.forEach(function(a){',start)
if end<0:
    raise SystemExit('fim do bloco de extração de artigos não encontrado')

new=r'''    /* PMAL_LAW_REF_V21 — art. singular = um artigo; arts. plural = lista/range somente por conectores explícitos */
    let arts=[],ar=/\b([Aa]rts?)\.?\s*/g,am;
    const artTokSrc='(\\d+[A-Fa-f]\\b|\\d+(?:\\s*\\.?\\s*[º°oO]\\.?)?(?:\\s*[-‐‑–—]\\s*[A-Fa-f])?)';
    while((am=ar.exec(clause))!==null){
      let rest=clause.slice(ar.lastIndex),first=new RegExp('^\\s*'+artTokSrc).exec(rest);
      if(!first)continue;
      let nums=[],a0=normArtToken(first[1]);
      if(a0)nums.push(a0);
      if(/s$/i.test(am[1])){
        let pos=first[0].length;
        while(true){
          let tail=rest.slice(pos);
          let nx=new RegExp('^\\s*(?:,|e|ou|a|até|[-‐‑–—])\\s*'+artTokSrc,'i').exec(tail);
          if(!nx)break;
          let an=normArtToken(nx[1]);
          if(an&&nums.indexOf(an)<0)nums.push(an);
          pos+=nx[0].length;
        }
      }
      if(nums.length)arts.push({start:am.index,nums:nums});
    }
'''

s=s[:start]+new+s[end:]
P.write_text(s,encoding='utf-8')
print('parser legal v2.1 aplicado: números soltos/anos não entram mais como artigos')
