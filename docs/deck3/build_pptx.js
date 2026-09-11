const pptxgen = require('pptxgenjs');
const fs = require('fs');
const IMG = '/home/user/VORN/docs/deck3/';
const P = new pptxgen();
P.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
const NAVY='1F2A37', RUST='B5442D', LIGHT='F1F4F7', MUTED='5B6570', LINE='C9D1D9', DARKCARD='2B3948', WHITE='FFFFFF', FOOT='7A8590';
const F='Meiryo';
const W=13.33, H=7.5, ML=0.75, MR=0.75;
const CW = W-ML-MR;

function slide(dark){ const s=P.addSlide(); s.background={color: dark?NAVY:WHITE}; s._dark=!!dark; return s; }
function title(s, text, opts={}){ s.addText(text,{x:ML,y:0.5,w:CW,h:opts.h||1.0,fontFace:F,fontSize:opts.size||24,bold:true,color:s._dark?WHITE:NAVY,valign:'top',isTextBox:true,margin:0,lineSpacingMultiple:1.15}); }
function foot(s, src, n){ s.addText(src||'',{x:ML,y:H-0.45,w:CW-0.6,h:0.3,fontFace:F,fontSize:8,color:s._dark?'AAB4BE':FOOT,isTextBox:true,margin:0,valign:'middle'}); s.addText(String(n),{x:W-MR-0.5,y:H-0.45,w:0.5,h:0.3,fontFace:F,fontSize:8,color:s._dark?'AAB4BE':FOOT,align:'right',isTextBox:true,margin:0,valign:'middle'}); }
function bullets(s, items, x,y,w,h, size=14, color){ s.addText(items.map((t,i)=>({text:t,options:{bullet:true,breakLine:i<items.length-1,paraSpaceAfter:8}})),{x,y,w,h,fontFace:F,fontSize:size,color:color||(s._dark?WHITE:NAVY),valign:'top',isTextBox:true,margin:0,lineSpacingMultiple:1.2}); }
function numbered(s, items, x,y,w,h, size=14){ s.addText(items.map((t,i)=>({text:t,options:{bullet:{type:'number'},breakLine:i<items.length-1,paraSpaceAfter:8}})),{x,y,w,h,fontFace:F,fontSize:size,color:NAVY,valign:'top',isTextBox:true,margin:0,lineSpacingMultiple:1.2}); }
function text(s, t, x,y,w,h, o={}){ s.addText(t,{x,y,w,h,fontFace:F,fontSize:o.size||12,color:o.color||(s._dark?WHITE:NAVY),bold:!!o.bold,align:o.align||'left',valign:o.valign||'top',isTextBox:true,margin:o.margin!==undefined?o.margin:0,lineSpacingMultiple:o.ls||1.25,fill:o.fill?{color:o.fill}:undefined,italic:!!o.italic}); }
function card(s, x,y,w,h, fill){ s.addShape(P.ShapeType.roundRect,{x,y,w,h,fill:{color:fill||(s._dark?DARKCARD:LIGHT)},line:{color:fill||(s._dark?DARKCARD:LIGHT)},rectRadius:0.08}); }
function box(s, x,y,w,h, label, sub, opts={}){ s.addShape(P.ShapeType.roundRect,{x,y,w,h,fill:{color:opts.fill||LIGHT},line:{color:opts.line||LINE,width:opts.lw||1, dashType:opts.dash||'solid'},rectRadius:0.06}); s.addText(sub?[{text:label,options:{bold:true,breakLine:true,fontSize:opts.size||12}},{text:sub,options:{fontSize:(opts.size||12)-3,color:opts.subColor||MUTED}}]:label,{x,y,w,h,fontFace:F,fontSize:opts.size||12,color:opts.color||NAVY,align:'center',valign:'middle',isTextBox:true,margin:0.05}); }
function arrow(s, x1,y1,x2,y2, color){ s.addShape(P.ShapeType.line,{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1)||0.001,h:Math.abs(y2-y1)||0.001,line:{color:color||NAVY,width:1.5,endArrowType:'triangle'},flipH:x2<x1,flipV:y2<y1}); }
function img(s, file, x,y,w, h){ const o={path:IMG+file,x,y,w}; if(h) o.h=h; s.addImage(o); s.addShape(P.ShapeType.rect,{x,y,w,h:h||imgH(file,w),line:{color:'D5DBE1',width:0.75},fill:{type:'none'}}); }
const sizes={ 'next.jpg':[1400,588],'rules.jpg':[1400,803],'form1.jpg':[1215,1120],'chat.jpg':[910,1210],'chat_s.jpg':[900,1197],'docs.jpg':[1400,635],'tk_sim.jpg':[1400,373],'tk_rules.jpg':[1400,560],'city_list.jpg':[1400,448],'city_detail.jpg':[1400,719],'city_pending.jpg':[1400,317],'city_reported.jpg':[1400,317],'yoko_p1.jpg':[910,1287],'yoko_form1.jpg':[910,1287],'tk_page.jpg':[1224,1650] };
function imgH(file,w){ const [pw,ph]=sizes[file]; return w*ph/pw; }
function cap(s, t, x,y,w,h){ text(s,t,x,y,w,h,{size:9.5,color:MUTED,ls:1.2}); }


function cover(s, file, x,y,w,h, pos){ const [pw,ph]=sizes[file]; const r=w/h; let cw=pw, ch=Math.round(pw/r); let cy=0; if(ch>ph){ ch=ph; cw=Math.round(ph*r);} if(pos==='center'){ cy=Math.round((ph-ch)/2);} s.addImage({path:IMG+file,x,y,w,h,sizing:{type:'crop',x:0,y:cy,w:cw,h:ch}}); s.addShape(P.ShapeType.rect,{x,y,w,h,line:{color:'D5DBE1',width:0.75},fill:{type:'none'}}); }
function callout(s, t, x,y,w,h){ s.addShape(P.ShapeType.roundRect,{x,y,w,h,fill:{color:RUST},line:{color:RUST},rectRadius:0.06,shadow:{type:'outer',blur:6,offset:2,angle:90,opacity:0.25,color:'000000'}}); text(s,t,x+0.12,y+0.08,w-0.24,h-0.16,{size:11,color:WHITE,valign:'middle'}); }
function frame(s, n, label, file, x,y,w,h){ s.addText([{text:n+' ',options:{color:RUST,bold:true,fontSize:11}},{text:label,options:{color:MUTED,fontSize:10}}],{x,y,w,h:0.28,fontFace:F,isTextBox:true,margin:0,valign:'middle'}); cover(s,file,x,y+0.3,w,h); }


// 1 表紙
{ const s=slide(true);
  text(s,'VORN Challenge 2026 応募作品',ML,1.5,7,0.4,{size:13,color:'AAB4BE'});
  text(s,'猫を世話する人の書類と期限を、\nAIが引き受ける。',ML,2.0,7.6,1.7,{size:32,bold:true,ls:1.2});
  text(s,'ネコノテ',ML,3.9,7.6,0.7,{size:28,bold:true});
  text(s,'チーム シーサーズ',ML,4.7,7,0.4,{size:12,color:'AAB4BE'});
  img(s,'next.jpg',8.6,1.6,4.1); cap(s,'市民面：開くと「次にやること」が出る',8.6,1.6+imgH('next.jpg',4.1)+0.05,4.1,0.3);
  foot(s,'',1);
}
// 2 自治体ごとに違う
{ const s=slide();
  title(s,'同じ「野良猫の不妊手術」でも、自治体ごとに要綱も様式も受付日も違う。',{h:0.7});
  text(s,'京都市は要綱16条＋6様式、登録3年、報告は毎年30日以内。高島市は毎月6日〜末日に申請して翌々月分のチケット、写真付き報告。函館市は個人不可で団体登録が要る。広島市は年度末まで、途中で増えた猫は別扱い。',ML,1.4,CW,0.8,{size:11.5});
  const w=3.75, g=0.31, y=2.35, h=3.6;
  cover(s,'yoko_p1.jpg',ML,y,w,h); cap(s,'京都市まちねこ活動支援要綱（PDF、16条）',ML,y+h+0.05,w,0.4);
  cover(s,'yoko_form1.jpg',ML+w+g,y,w,h); cap(s,'京都市 第1号様式 登録申請書（DOCX配布。要綱PDF内の様式）',ML+w+g,y+h+0.05,w,0.4);
  cover(s,'tk_page.jpg',ML+2*(w+g),y,w,h); cap(s,'高島市 環境政策課ページ本文（受付は毎月6日〜末日、翌々月分）',ML+2*(w+g),y+h+0.05,w,0.4);
  foot(s,'出典：京都市まちねこ活動支援事業ページ・要綱／高島市 環境政策課ページ／函館市・広島市は各自治体ページ',2);
}
// 3 無償依存
{ const s=slide();
  title(s,'市が出すのは手術・保護器・助言まで。あとは住民が無償でやる。',{h:0.7});
  text(s,'担い手は少なく、高齢で、後継がいない。',ML,1.6,6.4,0.5,{size:18,bold:true});
  card(s,ML,2.3,6.4,1.3); text(s,'「本来市役所の環境課や愛護センターがやるべきことを、ボランティアが無償でやっている」\n30代女性',ML+0.2,2.4,6.0,1.1,{size:12.5});
  card(s,ML,3.8,6.4,1.1); text(s,'「高齢者が多く、その方がいなくなったら引き継ぐ人がいない」\n50代女性',ML+0.2,3.9,6.0,0.9,{size:12.5});
  const bx=7.9, by=1.7;
  box(s,bx,by,1.5,0.85,'自治体','手術・保護器・助言'); box(s,bx+1.7,by,1.5,0.85,'基金','チケット・規約'); box(s,bx+3.4,by,1.5,0.85,'病院','予約枠・持込日');
  arrow(s,bx+0.75,by+0.9,bx+2.2,by+3.0); arrow(s,bx+2.45,by+0.9,bx+2.45,by+3.0); arrow(s,bx+4.15,by+0.9,bx+2.7,by+3.0);
  s.addShape(P.ShapeType.ellipse,{x:bx+1.75,y:by+3.0,w:1.4,h:1.4,fill:{color:RUST},line:{color:RUST}}); text(s,'住民',bx+1.75,by+3.0,1.4,1.4,{size:16,color:WHITE,align:'center',valign:'middle'});
  text(s,'無償・少数・高齢・後継なし',bx+0.6,by+4.5,3.7,0.35,{size:11,color:MUTED,align:'center'});
  foot(s,'出典：福岡県「ペットや飼い主のいない猫の過剰繁殖等の対策について」県民モニター調査（N=349、2022年実施と推定）',3);
}
// 4 現状の手間
{ const s=slide();
  title(s,'一つのコロニーを終わらせるために、一人がやっていること。',{h:0.7});
  text(s,'京都市の場合。同意が取れた後から3年更新まで、11段。',ML,1.15,CW,0.3,{size:11,color:MUTED});
  { const i=0; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'①',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'要綱を読んで自分の場合を探す',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=1; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'FBE9E5'); text(s,'②',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'同一世帯でない住民2人＋京都市民1人を集める',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=2; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'FBE9E5'); text(s,'③',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'町内会に説明し日付を控える',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=3; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'④',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'第1号様式・第6号様式を手書き',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=4; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'F1F4F7'); text(s,'⑤',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'周辺地図を描く',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=5; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'⑥',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'分からないことは平日にセンターへ電話',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=6; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'⑦',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'受付日と有効期限を自分で管理',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=7; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'FBE9E5'); text(s,'⑧',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'第4号様式、保護器を借りて捕獲、持込',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=8; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'⑨',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'1年後に第5号様式を登録日と同月日から30日以内',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=9; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'⑩',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'3年後に第2号様式を満了30日前から',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }
  { const i=10; const x=ML+(i%6)*1.98, y=1.5+Math.floor(i/6)*1.75; card(s,x,y,1.85,1.6,'E4EEF9'); text(s,'⑪',x+0.12,y+0.08,1.6,0.35,{size:16,bold:true,color:RUST}); text(s,'自分が倒れた時の引継ぎ',x+0.12,y+0.45,1.62,1.1,{size:10.5}); }

  s.addText([{text:' 青 ',options:{fill:{color:'1F4E8A'},color:WHITE,fontSize:9,bold:true}},{text:'  要綱と期限に関わる事務。8枚目で置き換え対象になる    ',options:{fontSize:11,color:MUTED}},{text:' 赤 ',options:{fill:{color:RUST},color:WHITE,fontSize:9,bold:true}},{text:'  人がやること（人集め・説明・捕獲）    ',options:{fontSize:11,color:MUTED}},{text:' 灰 ',options:{fill:{color:MUTED},color:WHITE,fontSize:9,bold:true}},{text:'  その他',options:{fontSize:11,color:MUTED}}],{x:ML,y:5.2,w:CW,h:0.4,fontFace:F,isTextBox:true,margin:0,valign:'middle'});
  foot(s,'出典：京都市まちねこ活動支援要綱（第2条・第5条・第6条・第9条・第12条）',4);
}
// 5 摩擦①
{ const s=slide();
  title(s,'手間のどこで止まっても、猫は待ってくれない。',{h:0.7});
  bullets(s,['受付を1回逃す → 手術は1か月遅れ → 次の出産（年2〜3回、一度に4〜6匹）が先に来る','制度を知らず自腹で手術：活動しているのに支援制度を知らない 10.0% ＞ 知っている 8.6%','報告を落とす → 京都市要綱第7条3項、職権で抹消','担い手が倒れる → どの猫が手術済みか、餌場がどこか、情報ごと消える','効くと分かっている（京都市：収容44%減、路上死亡28%減、手術94→1,612頭）のに、活動中の地域数は3年横ばい'],ML,1.5,5.8,3.6,11.5);
  card(s,ML,5.25,5.8,1.0); text(s,'「いつ妊娠するか分からないので受付期間を限定しないでほしい」（40代女性）',ML+0.2,5.33,5.4,0.85,{size:11.5});
  const fx=7.0, fy=2.4, fw=5.6;
  text(s,'▮ 制度の受付窓（月1回・数日）→ 使えるのは翌月',fx,fy-0.45,fw,0.3,{size:11});
  s.addShape(P.ShapeType.line,{x:fx,y:fy+0.3,w:fw,h:0,line:{color:LINE,width:2}});
  for(let i=0;i<12;i++){ s.addShape(P.ShapeType.rect,{x:fx+i*(fw/12),y:fy+0.15,w:0.07,h:0.3,fill:{color:NAVY},line:{color:NAVY}}); }
  ['4月','7月','10月','1月','4月'].forEach((m,i)=>text(s,m,fx+i*(fw/4)-0.25,fy+0.5,0.5,0.3,{size:10,color:MUTED,align:'center'}));
  [0.13,0.5,0.87].forEach(f=>s.addShape(P.ShapeType.ellipse,{x:fx+f*fw-0.11,y:fy+1.1,w:0.22,h:0.22,fill:{color:RUST},line:{color:RUST}}));
  text(s,'● 出産（年2〜3回、一度に4〜6匹）',fx,fy+1.5,fw,0.3,{size:11,color:RUST});
  text(s,'窓を1回逃すと手術は1か月遅れ、次の出産が先に来る。',fx,fy+1.9,fw,0.35,{size:11.5});
  foot(s,'出典：どうぶつ基金 チケットFAQ・規約／福岡県調査／京都市10年評価／京都市要綱 第7条',5);
}

// 6 なぜ解決されてこなかったか
{ const s=slide();
  title(s,'非営利で金が回らず、自治体ごとに違うので個別開発も成立しない。だから人手しかなかった。',{h:0.9});
  text(s,'1自治体の担い手は数十〜数百人。協働自治体は298で要綱は全部違う。誰も作らず、現場は電話・LINE・Excel・紙のまま。',ML,1.6,CW,0.6,{size:13});
  text(s,'それぞれの悩み',ML,2.35,CW,0.3,{size:11,color:MUTED});
  [['ボランティア','要綱が読めない。期限を忘れる。電話が平日しか通じない。'],['市の職員','不備で往復。電話の一次対応。登録地域の現況が報告頼み。'],['近隣住民','苦情を出しても行政は収容しない。活動が始まるまで解決手段がない。'],['病院・センター','持込頭数と時期が読めない。']].forEach((c,i)=>{ const x=ML+i*3.0; card(s,x,2.75,2.8,2.6); text(s,c[0],x+0.2,2.9,2.4,0.4,{size:15,bold:true}); text(s,c[1],x+0.2,3.4,2.4,1.8,{size:12}); });
  foot(s,'出典：どうぶつ基金 2022年度実績（298行政）／堺市 猫の困りごとページ',6);
}
// 7 問い
{ const s=slide(true); text(s,'人手を増やさずに、この手間を消せるか。',ML,3.0,CW,1.2,{size:34,bold:true,align:'center',valign:'middle'}); foot(s,'',7); }
// 8 AIの特性
{ const s=slide();
  title(s,'AIは自然言語の規則をそのまま読み、個別の事情にまとめ直し、何件でも追い続けられる。',{h:0.9});
  [['読める','要綱PDF・様式DOCX・FAQを構造化せずそのまま読み、条件と期限を引く。'],['まとめ直せる','「この場所・この頭数・この自治体・今日」に翻訳して返す。'],['追い続ける','登録日から期限を計算し、期日に促す。忘れない。'],['作り直さない','自治体が変われば要綱を差し替えるだけ。規則をコードに書かない。']].forEach((c,i)=>{ const x=ML+i*3.0; card(s,x,1.6,2.8,2.5); text(s,c[0],x+0.2,1.75,2.4,0.4,{size:15,bold:true}); text(s,c[1],x+0.2,2.25,2.4,1.7,{size:12}); });
  card(s,ML,4.5,CW,1.3); s.addText([{text:'4枚目の作業のうち、',options:{fontSize:16}},{text:'①⑥⑦⑨⑩⑪',options:{fontSize:16,bold:true,color:RUST}},{text:' は人手ではなくこれで置き換えられる。',options:{fontSize:16,breakLine:true}},{text:'②人集め・③町内会への説明・⑧捕獲は人がやる。',options:{fontSize:13,color:MUTED}}],{x:ML+0.25,y:4.6,w:CW-0.5,h:1.1,fontFace:F,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.3});
  foot(s,'',8);
}
// 9 今回作ったもの
{ const s=slide();
  title(s,'地域猫に限定して、一例を作った。会話で入れると、次にやることと書類が出て、市の台帳に残る。',{h:0.9});
  const y=1.65, w=3.75, g=0.31;
  frame(s,'①','会話で入れる','chat_s.jpg',ML,y,w,4.2);
  frame(s,'②','次にやることと様式が出る','next.jpg',ML+w+g,y,w,1.58); cover(s,'form1.jpg',ML+w+g,y+2.0,w,2.5);
  frame(s,'③','市の台帳に残る','city_list.jpg',ML+2*(w+g),y,w,1.2); cover(s,'city_pending.jpg',ML+2*(w+g),y+1.62,w,0.85); cap(s,'K-2026-010 が「申請中」で載り、報告後に「報告済」になる',ML+2*(w+g),y+2.55,w,0.6);
  foot(s,'プロトタイプ（Streamlit／Anthropic API）。京都市・高島市で動作。画面はすべて実機。',9);
}
// 10 話す
{ const s=slide();
  title(s,'ボランティアは要綱を読まない。場所と頭数を話すだけ。',{h:0.7});
  cover(s,'chat.jpg',ML,1.45,5.4,5.1);
  callout(s,'「11頭くらい、3人でやります」と話すと、AIが要綱第2条を引いて「11頭なので京都市民3名以上」と返し、次に聞くべき項目（餌場・トイレ・町内会）へ進む。',6.6,1.9,6.0,1.1);
  text(s,'入力は自然文。要綱の条件はAI側が持つ。集めるのは第1号様式・第6号様式に必要な項目だけ。\n\n捕獲の手順・自治会の説得・里親探し・子猫の育て方を聞かれると「範囲外」と断る。',6.6,3.3,6.0,2.0,{size:12,color:MUTED});
  foot(s,'画面はプロトタイプ。デモ用の架空コロニー（左京区・11頭・活動者3名）',10);
}
// 11 判定＋次にやること
{ const s=slide();
  title(s,'出す前に不足が条文付きで分かり、開くと次にやることが1つ出る。',{h:0.7});
  cover(s,'rules.jpg',ML,1.45,5.9,4.4); cap(s,'判定。「周辺地図は別途添付」は要綱第5条、「登録後に第4号様式」は第9条から。13件の規則に出典と引用が付く。',ML,5.9,5.9,0.5);
  img(s,'next.jpg',6.9,1.45,5.7); callout(s,'期限は登録日から要綱の期日ルールで自動計算。報告は同月日から30日以内、更新は満了30日前から。',8.9,1.55,3.6,0.95);
  cap(s,'次にやること。台帳の状態が変わると項目が入れ替わる。',6.9,1.45+imgH('next.jpg',5.7)+0.05,5.7,0.3);
  card(s,6.9,4.4,5.7,1.2); text(s,'提出前は「提出」、登録後は「周知」「手術申請」「報告期限」「満了日」。担い手が要綱と期限を覚えておく必要がない。',7.1,4.5,5.3,1.0,{size:12});
  foot(s,'画面はプロトタイプ（京都市プロファイル）。規則はコードに書いていない。',11);
}
// 12 様式
{ const s=slide();
  title(s,'京都市配布のDOCXに、そのまま転記される。',{h:0.7});
  img(s,'form1.jpg',ML,1.4,5.7);
  callout(s,'様式のセル構造（表・行・列）をAIが読み、どのセルに何を書くかを決めて転記する。',6.8,1.45,5.8,0.8);
  text(s,'第6号（実施計画書）・第4号（手術実施申請書）・第5号（活動状況報告書）も同様。印刷して出すだけ。',6.8,2.45,5.8,0.7,{size:13.5});
  cover(s,'docs.jpg',6.8,3.3,5.8,2.2); cap(s,'画面上の項目一覧。「要確認」は記載例と照らして確認が要る欄。',6.8,5.55,5.8,0.4);
  foot(s,'左：第1号様式 まちねこ活動登録申請書（配布 touroku.docx）に転記した結果',12);
}
// 13 市の職員
{ const s=slide();
  title(s,'市は、更新が切れそうな地域を、切れる前に知る。',{h:0.7});
  img(s,'city_list.jpg',ML,1.4,7.4); callout(s,'更新待ち → 期限超過。届出なしで切れる地域が見える。',5.2,2.25,2.9,0.7);
  cover(s,'city_detail.jpg',ML,1.4+imgH('city_list.jpg',7.4)+0.15,7.4,2.4);
  card(s,8.5,1.4,4.1,3.0); text(s,'不備のない申請だけ届く。\n\n「3年横ばい」の中身（終了か、届出なしの脱落か）が初めて分かる。\n\n台帳は申請と報告の副産物で、引継ぎ用の入力はさせない。',8.7,1.55,3.7,2.7,{size:12.5});
  cap(s,'状態は要綱の期日ルール（報告は登録日と同月日から30日以内、更新は満了日の30日前から）と報告履歴から計算。',8.5,4.55,4.1,0.7);
  foot(s,'画面はプロトタイプ（自治体面：京都市医療衛生センター）。台帳の他4件はダミー。出典：京都市要綱 第7条3項',13);
}
// 14 以前／今
{ const s=slide();
  title(s,'4枚目の手間は、こう変わる。',{h:0.7});
  const rows=[[{text:'以前',options:{bold:true,fill:{color:LIGHT}}},{text:'今',options:{bold:true,fill:{color:LIGHT}}}],['①要綱を読む',{text:'話すと条文を引いて返す',options:{fill:{color:'F1F9F3'}}}],['④様式を手書き',{text:'DOCXに自動転記',options:{fill:{color:'F1F9F3'}}}],['⑤不備で戻される',{text:'提出前に分かる',options:{fill:{color:'F1F9F3'}}}],['⑥平日に電話',{text:'いつでも聞ける',options:{fill:{color:'F1F9F3'}}}],['⑦受付・期限を記憶',{text:'自動計算、期日に促す（高島市：逃すと+30日、を出す前に示す）',options:{fill:{color:'F1F9F3'}}}],['⑨⑩報告・更新を忘れて抹消',{text:'期日に促し、話すだけで様式が出る',options:{fill:{color:'F1F9F3'}}}],['⑪倒れたら消える',{text:'市の台帳に残る',options:{fill:{color:'F1F9F3'}}}]];
  s.addTable(rows,{x:ML,y:1.4,w:CW,colW:[5.2,6.63],fontFace:F,fontSize:12.5,color:NAVY,border:{type:'solid',color:LINE,pt:0.75},rowH:0.46,margin:0.08,valign:'middle'});
  text(s,'残るもの：②人集め ③町内会への説明 ⑧捕獲。ここは人。',ML,5.3,CW,0.4,{size:13,color:MUTED});
  foot(s,'右列は規則から導ける変化のみ。審査・手術日の待ちは消えない。',14);
}
// 15 横展開
{ const s=slide();
  title(s,'要綱を差し替えるだけで別の自治体に対応する。規則はコードに1行も書いていない。',{h:0.9});
  cover(s,'tk_sim.jpg',ML,1.6,CW,2.4); callout(s,'+30日。この受付（毎月6日〜末日）を逃すと、チケットの有効月が1か月遅れる。',ML+0.2,3.2,4.6,0.7);
  cover(s,'tk_rules.jpg',ML,4.2,6.4,1.6); cap(s,'高島市の資料から抽出した規則に照らした判定。受付の値は市HP本文から抽出。交付要綱PDFは未取得。',ML,5.85,6.4,0.5);
  text(s,'京都市（登録型）と高島市（基金チケット型）は仕組みが違うが、同じ画面・同じコード。\n\n住民が申請し、期限があり、報告と更新があり、担い手が無償で属人的な制度は、行政の中に他にもある。',7.4,4.2,5.2,2.0,{size:12.5});
  foot(s,'画面はプロトタイプ（高島市プロファイル）。出典：高島市 環境政策課ページ／どうぶつ基金 チケットFAQ・登録規約',15);
}
// 16 主題
{ const s=slide();
  title(s,'自治体ごとに違う自然言語のルールを、AIが個人の代わりに読み、追い続ける。',{h:0.9});
  text(s,'このエンジンが読んでいるのは「猫の要綱」ではなく「自治体が自然言語で公開している要綱と様式」。\n\n猫は、効果が実証済みで、担い手が最も薄く、市が障壁を認めた場所だから、ここから始めた。',ML,1.7,6.4,3.0,{size:15});
  const fx=8.0, fy=1.9;
  box(s,fx+1.0,fy,2.4,0.9,'同じエンジン',null,{fill:NAVY,line:NAVY,color:WHITE,size:14});
  box(s,fx,fy+1.9,1.5,0.7,'京都市',null,{}); box(s,fx+1.5,fy+1.9,1.5,0.7,'高島市',null,{}); box(s,fx+3.0,fy+1.9,1.3,0.7,'……',null,{fill:WHITE,dash:'dash',color:MUTED});
  [[fx+1.6,fy+0.9,fx+0.75,fy+1.9],[fx+2.2,fy+0.9,fx+2.25,fy+1.9],[fx+2.8,fy+0.9,fx+3.65,fy+1.9]].forEach(a=>s.addShape(P.ShapeType.line,{x:Math.min(a[0],a[2]),y:a[1],w:Math.abs(a[2]-a[0])||0.01,h:a[3]-a[1],line:{color:MUTED,width:1.5},flipH:a[2]<a[0]}));
  text(s,'要綱一式のフォルダを置くだけ',fx,fy+2.8,4.4,0.3,{size:10,color:MUTED,align:'center'});
  foot(s,'',16);
}
// 17 届け方・指標・限界・チーム
{ const s=slide();
  title(s,'京都市で立ち上げ、動物病院と苦情窓口から届ける。',{h:0.7});
  [['届け方','京都市で立ち上げ。動物病院（京都市獣医師会がまちねこ活動をサポート）と苦情窓口から。払い手は市の既存予算の事務コスト。'],['指標','申請から手術までの日数／登録継続率（職権抹消の減少）／引継ぎ後に継続した地域数／センター収容の子猫数'],['限界','当事者ヒアリング未実施（通過後にセンター・基金へ）／高島市要綱PDF未取得／実APIの応答品質は検証中で、掲載画面はモック応答で撮影']].forEach((c,i)=>{ const x=ML+i*4.0; card(s,x,1.5,3.8,2.5); text(s,c[0],x+0.2,1.65,3.4,0.4,{size:15,bold:true}); text(s,c[1],x+0.2,2.15,3.4,1.75,{size:12}); });
  card(s,ML,4.3,CW,1.5); text(s,'チーム シーサーズ',ML+0.2,4.42,CW-0.4,0.4,{size:15,bold:true}); text(s,'技術構成：Python／Streamlit／Anthropic API（Claude）／python-docx。京都市・高島市の2プロファイルで動作。要綱の規則はコードに書かず、資料フォルダから毎回抽出。日付の計算だけコード側。',ML+0.2,4.9,CW-0.4,0.8,{size:12});
  foot(s,'出典：京都市獣医師会 まちねこページ／京都市10年評価／どうぶつ基金 2022年度実績',17);
}
// 付録A
{ const s=slide();
  title(s,'付録A　一次情報の出典',{size:20,h:0.6});
  const c1='京都市（デモ対象）\n\nまちねこ活動支援事業\nhttps://www.city.kyoto.lg.jp/hokenfukushi/page/0000189400.html\n\n要綱（令和6年4月1日改正）\nhttps://www.city.kyoto.lg.jp/hokenfukushi/cmsfiles/contents/0000189/189400/yoko060401.pdf\n\n第1号様式 …/touroku.docx／第6号様式 …/jissikeikaku.docx／記載例 …/rei_touroku.pdf, …/rei_jissikeikaku.pdf／参考様式 …/osirase.pdf（同ディレクトリ）\n\n10年間の事業評価\nhttps://www.city.kyoto.lg.jp/hokenfukushi/page/0000277536.html\n\n京都市獣医師会\nhttps://www.kyoto-shiju.or.jp/machineko.html';
  const c2='どうぶつ基金・基金型自治体\n\nチケットFAQ\nhttps://sakuraneko-tnr.doubutukikin.or.jp/faq\n\n登録・チケット規約\nhttps://sakuraneko-tnr.doubutukikin.or.jp/about/register\n\n事業概要\nhttps://www.doubutukikin.or.jp/activity/sakuraneko-surgery/\n\n2022年度実績\nhttps://www.doubutukikin.or.jp/activitynews/20230727/37090/\n\n高島市 環境政策課\nhttps://www.city.takashima.lg.jp/soshiki/kankyobu/kankyoseisakuka/2924.html\n\n大網白里市\nhttps://www.city.oamishirasato.lg.jp/0000014129.html';
  const c3='当事者の声・背景\n\n福岡県 県民モニター調査（N=349。実施年は資料に明記なし、自由記述から2022年実施と推定）\nhttps://www.pref.fukuoka.lg.jp/uploaded/attachment/186043.pdf\n\n堺市（猫は法令上捕獲根拠がなく行政は収容しない）\nhttps://www.city.sakai.lg.jp/kurashi/dobutsu/dogcat/komarigoto/inunekokomaru.html\n\n環境省 犬・猫の引取り及び負傷動物の収容状況\nhttps://www.env.go.jp/nature/dobutsu/aigo/2_data/statistics/dog-cat.html\n\n数字の扱い\n本資料の数字はすべて上記の一次情報から引用。事業の効果（収容減・苦情減）は京都市の事業の効果であり、本プロダクトの効果ではない。本プロダクトが変えるのは「申請から手術までの日数」「登録の継続率」「担い手交代後の継続」。';
  [c1,c2,c3].forEach((c,i)=>text(s,c,ML+i*3.98,1.3,3.8,5.6,{size:8.5,ls:1.3}));
  foot(s,'',  'A');
}
// 付録B
{ const s=slide();
  title(s,'付録B　京都市まちねこ活動支援要綱 抜粋（令和6年4月1日改正）',{size:20,h:0.6});
  const b1='第2条⑵　活動は、同一世帯員ではない地域住民２人以上（ただし、その管理する野良猫が１０頭以上の場合にあっては同一世帯員ではない地域住民２人を含む京都市民３人以上）による団体を構成して行うものであること。\n\n第5条　「まちねこ活動登録申請書」（第１号様式）に、「まちねこ活動実施計画書」（第６号様式）及び次に掲げる事項を示した周辺地図を添えて、医療衛生センター長に提出するものとする。⑴活動地域の範囲 ⑵給餌の場所 ⑶野良猫用のトイレの場所\n第5条3　登録の有効期間は、登録の日から３年間とする。\n\n第6条2　登録を更新しようとする団体は、「まちねこ活動登録更新申請書」（第２号様式）及び「実施計画書」を、従前の登録の有効期間の満了の日の３０日前から満了日までに医療衛生センター長に提出するものとする。\n\n第7条3　医療衛生センター長は、期限までに第６条の更新が行われなかったもの又は活動の実態が認められない若しくは効果がないと思料するものについて、まちねこ活動団体に、第１項に規定する届出を行うよう求め、又は必要な調査を行ったうえ職権で登録を抹消することができる。';
  const b2='第9条　まちねこの避妊去勢手術を依頼しようとするときは、まちねこ避妊去勢手術実施申請書（第４号様式）を医療衛生センター長に提出するものとする。\n第10条　避妊去勢手術の実施の日時は、動物愛護センターが医療衛生センター長を通じ、まちねこ活動団体に通知する。\n\n第12条　まちねこ活動団体は、１年ごとに、医療衛生センター長に対して、「まちねこ活動状況報告書」（第５号様式）を提出し、まちねこの管理の状況について、報告しなければならない。\n第12条2　前項に規定する報告は、登録をした日の属する年の翌年以降、毎年、登録した日と同月日から３０日以内に行うものとする。\n\n様式一覧　第1号 登録申請書／第2号 登録更新申請書／第3号 廃止届出書／第4号 避妊去勢手術実施申請書／第5号 活動状況報告書／第6号 活動実施計画書／参考様式 近隣の皆さまへ（お知らせ）\n\n記載例の注記（R6.4.1〜）　代表者の署名・押印不要。管理する猫が10頭以上の場合、地域住民2名以上のほかに京都市民1名以上の登録が必要。3人目の活動者は同一町内でなくとも可。';
  text(s,b1,ML,1.3,5.8,5.6,{size:9.5,ls:1.35}); text(s,b2,6.85,1.3,5.75,5.6,{size:9.5,ls:1.35});
  foot(s,'出典：京都市まちねこ活動支援要綱（yoko060401.pdf）／記載例 rei_touroku.pdf','B');
}
P.writeFile({fileName:'/home/user/VORN/docs/deck3/nekonote_VORN2026.pptx'}).then(f=>console.log('written',f));
