const pptxgen = require('pptxgenjs');
const fs = require('fs');
const IMG = '/home/user/VORN/docs/deck/';
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
const sizes={ 'next.jpg':[940,325],'rules_s.jpg':[940,335],'form1.jpg':[1215,1120],'muni_list.jpg':[940,260],'muni_detail.jpg':[940,360],'tk_sim.jpg':[940,300],'tk_rules_s.jpg':[940,300] };
function imgH(file,w){ const [pw,ph]=sizes[file]; return w*ph/pw; }
function cap(s, t, x,y,w,h){ text(s,t,x,y,w,h,{size:9.5,color:MUTED,ls:1.2}); }

// 1 表紙
{ const s=slide(true);
  text(s,'VORN Challenge 2026 応募作品',ML,1.7,7,0.4,{size:13,color:'AAB4BE'});
  text(s,'自治体ごとに違う自然言語のルールを、\nAIが個人の代わりに読み、追い続ける。',ML,2.2,7.6,1.7,{size:30,bold:true,ls:1.2});
  text(s,'【製品名】 ── 地域猫活動の申請・日程・報告を、担い手に代わって回す',ML,4.1,7.6,0.5,{size:16});
  text(s,'チーム【チーム名】',ML,4.7,7,0.4,{size:12,color:'AAB4BE'});
  img(s,'next.jpg',8.6,1.4,4.1); cap(s,'市民面：開くと「次にやること」が出る',8.6,1.4+imgH('next.jpg',4.1)+0.05,4.1,0.3);
  foot(s,'',1);
}
// 2 構造
{ const s=slide();
  title(s,'行政の制度は各層が合理的で、それを1件分に合成する役だけが、無報酬の個人に落ちている。');
  bullets(s,['制度は自治体・基金・病院がそれぞれ作る。どれも単体では合理的。','しかし「この人・この場所・この自治体で、次に何をいつまでに」を組み立てて追う役は、どの層にもない。','その役は現場の個人が無報酬で引き受け、個人が抜けると制度ごと止まる。','人手不足の領域ほど、この構造が露出する。'],ML,1.7,6.6,2.6);
  card(s,ML,4.4,6.6,1.25); text(s,'「本来市役所の環境課や愛護センターがやるべきことを、ボランティアが無償でやっている」\n福岡県 県民モニター調査・30代女性',ML+0.2,4.5,6.2,1.05,{size:12});
  const bx=8.0, by=1.8;
  box(s,bx,by,1.5,0.85,'自治体','要綱・様式・期限'); box(s,bx+1.7,by,1.5,0.85,'基金','受付日・チケット・報告'); box(s,bx+3.4,by,1.5,0.85,'病院','予約枠・持込日');
  arrow(s,bx+0.75,by+0.9,bx+2.2,by+3.0); arrow(s,bx+2.45,by+0.9,bx+2.45,by+3.0); arrow(s,bx+4.15,by+0.9,bx+2.7,by+3.0);
  s.addShape(P.ShapeType.ellipse,{x:bx+1.75,y:by+3.0,w:1.4,h:1.4,fill:{color:RUST},line:{color:RUST}});
  text(s,'個人',bx+1.75,by+3.0,1.4,1.4,{size:16,color:WHITE,align:'center',valign:'middle'});
  text(s,'無報酬・1人・抜けると止まる',bx+0.6,by+4.5,3.7,0.35,{size:11,color:MUTED,align:'center'});
  foot(s,'出典：福岡県「ペットや飼い主のいない猫の過剰繁殖等の対策について」県民モニター調査（N=349、2022年実施と推定）',2);
}
// 3 なぜ地域猫
{ const s=slide();
  title(s,'この構造が一番むき出しなのが地域猫活動。効果は実証済みで、担い手は少なく、高齢で、後継がいない。');
  bullets(s,['猫は法令上の捕獲根拠がなく、行政は収容しない。行政が事実上使える手段は地域猫活動（不妊手術と地域管理）だけ。','効果は実証済み。京都市では活動地域の拡大とともに、センター収容の所有者不明猫が44%減、路上死亡が28%減。','実行は無償の住民に全面依存。市が出すのは手術・保護器・助言まで。'],ML,1.7,6.2,2.5);
  card(s,ML,4.35,6.2,1.55); text(s,'「世話する人がいなくて対策が進まなかった。他に出てこなければいずれ途切れる」（70代男性）\n「高齢者が多く、その方がいなくなったら引き継ぐ人がいない」（50代女性）\n福岡県 県民モニター調査',ML+0.2,4.45,5.8,1.35,{size:11.5});
  const st=[['94 → 1,612','年間の手術頭数（H22 → R1）'],['5,169 → 3,715','路上死亡の猫（H26 → R1）'],['1,470 → 685','苦情件数（H21 → H25年度）'],['−44%','センター収容の所有者不明猫']];
  st.forEach((v,i)=>{ const x=7.4+(i%2)*2.65, y=1.7+Math.floor(i/2)*1.7; card(s,x,y,2.5,1.55); text(s,v[0],x+0.15,y+0.15,2.2,0.8,{size:i==3?30:22,bold:true,color:i==3?RUST:NAVY,valign:'middle'}); text(s,v[1],x+0.15,y+1.0,2.2,0.45,{size:9.5,color:MUTED}); });
  cap(s,'京都市まちねこ活動支援事業（平成22年度開始）の10年評価より。収容される猫の多くは生まれたばかりで自活できない子猫。',7.4,5.2,5.15,0.6);
  foot(s,'出典：京都市「まちねこ活動支援事業の10年間の事業評価」／堺市 猫の困りごとページ／福岡県調査',3);
}
// 4 問題
{ const s=slide();
  title(s,'少ない担い手が制度の時間軸に合わせて動かないと、猫の方が先に増える。',{h:0.7});
  numbered(s,['受付期間：基金チケットは申請が毎月1〜5日、翌月1か月のみ有効。自治体はさらに独自の期日（高島市は翌々月分）。「いつ妊娠するか分からないので受付期間を限定しないでほしい」（福岡県調査・40代女性）','自治体差：出る市町村と出ない市町村、要綱も様式も別。協力病院は全国200件弱。「病院が遠すぎて連れていけない」','継続：年次報告・3年更新・完了報告を落とせば制度から外れる。京都市要綱では更新がなければ職権で抹消。','引継ぎ：担い手が倒れると、どの猫が手術済みか・餌場はどこかの情報ごと消える。'],ML,1.4,6.6,3.6,13);
  text(s,'結果：活動しているのに支援制度を知らない人（35件・10.0%）が知っている人（30件・8.6%）より多く、自腹で手術している人がいる。京都市は毎年新規地域があるのに活動中の地域数は3年横ばい。生まれた子猫がセンターに入る。',ML,5.1,6.6,1.2,{size:11.5,bold:false});
  // timeline figure
  const fx=8.0, fy=2.6, fw=4.6;
  text(s,'▮ 制度の受付窓（月1回・数日）→ 使えるのは翌月',fx,fy-0.4,fw,0.3,{size:10.5});
  s.addShape(P.ShapeType.line,{x:fx,y:fy+0.3,w:fw,h:0.001,line:{color:LINE,width:2}});
  for(let i=0;i<12;i++){ s.addShape(P.ShapeType.rect,{x:fx+i*(fw/12),y:fy+0.15,w:0.06,h:0.3,fill:{color:NAVY},line:{color:NAVY}}); }
  ['4月','7月','10月','1月','4月'].forEach((m,i)=>text(s,m,fx+i*(fw/4)-0.25,fy+0.5,0.5,0.3,{size:9.5,color:MUTED,align:'center'}));
  [0.13,0.5,0.87].forEach(f=>s.addShape(P.ShapeType.ellipse,{x:fx+f*fw-0.1,y:fy+1.05,w:0.2,h:0.2,fill:{color:RUST},line:{color:RUST}}));
  text(s,'● 出産（年2〜3回、一度に4〜6匹）',fx,fy+1.4,fw,0.3,{size:10.5,color:RUST});
  text(s,'窓を1回逃すと手術は1か月遅れ、次の出産が先に来る。',fx,fy+1.75,fw,0.35,{size:10.5});
  foot(s,'出典：どうぶつ基金 チケットFAQ・規約／高島市／京都市要綱 第7条／福岡県調査／京都市10年評価',4);
}
// 5 原因
{ const s=slide();
  title(s,'欠けているのは情報でも予算でもなく、「次に何をいつまでに」を組み立てて追い続ける役。',{h:0.7});
  bullets(s,['必要な知識は、要綱・FAQ・規約として全部自然言語で公開されている。','行政はそれを平日の電話で助言している（京都市医療衛生センターは4方面）。人手が限られ、担い手が代わればゼロからになる。','現場の道具は電話・LINE・Excel・紙。期限は人の記憶。','京都市は令和6年4月に要件を緩和（町内会長署名の廃止）。市自身が「手続きが障壁」と認めて手を入れた。'],ML,1.5,6.4,4.0);
  const bx=7.7, by=1.7;
  s.addShape(P.ShapeType.roundRect,{x:bx,y:by,w:1.9,h:2.9,fill:{color:LIGHT},line:{color:LINE},rectRadius:0.08});
  text(s,'公開されている知識\n\n要綱 PDF（16条＋6様式）\n様式 DOCX・記載例\n基金 FAQ・規約\n協力病院一覧\n市HPの注意事項',bx+0.15,by+0.15,1.7,2.6,{size:11,ls:1.35});
  s.addShape(P.ShapeType.roundRect,{x:bx+3.2,y:by,w:1.9,h:2.9,fill:{color:LIGHT},line:{color:LINE},rectRadius:0.08});
  text(s,'担い手\n\nこの場所・この頭数\nこの自治体\n今日の日付\n前回の報告\n誰が引き継ぐか',bx+3.35,by+0.15,1.7,2.6,{size:11,ls:1.35});
  s.addShape(P.ShapeType.roundRect,{x:bx+2.05,y:by+0.95,w:1.0,h:0.9,fill:{type:'none'},line:{color:RUST,width:1.5,dashType:'dash'},rectRadius:0.08});
  text(s,'合成と\n追跡',bx+2.05,by+0.95,1.0,0.9,{size:11.5,color:RUST,align:'center',valign:'middle'});
  text(s,'この空白を、今は無償の誰か1人が埋めている',bx,by+3.05,5.1,0.3,{size:10,color:MUTED,align:'center'});
  foot(s,'出典：京都市まちねこ活動支援事業ページ／京都市まちねこ活動支援要綱（令和6年4月1日改正）',5);
}
// 6 解決策
{ const s=slide(true);
  title(s,'担い手には「次にやること」を、市には「途切れない台帳」を。',{h:0.7});
  card(s,ML,1.5,3.9,2.6); text(s,'市民面（担い手）',ML+0.2,1.65,3.5,0.4,{size:15,bold:true}); text(s,'場所と頭数を会話で入れると、その自治体の要綱を読んで「使える制度・条件・次の受付・必要書類」を返す。様式を埋め、日程を組み、期限が来れば促し、報告を出す。',ML+0.2,2.1,3.5,1.9,{size:11.5});
  text(s,'AI の役割',4.95,1.55,3.4,0.3,{size:11,color:'AAB4BE',align:'center'});
  text(s,'自治体ごとに違う自然言語の要綱を、個別の事情に翻訳し、追い続ける',4.95,1.9,3.4,0.8,{size:12.5,align:'center'});
  arrow(s,5.1,3.1,8.2,3.1,'AAB4BE'); text(s,'要綱 → 個別の日程・様式',4.95,2.75,3.4,0.3,{size:10,align:'center'});
  arrow(s,8.2,3.7,5.1,3.7,'AAB4BE'); text(s,'申請・報告 → 一覧',4.95,3.8,3.4,0.3,{size:10,align:'center'});
  card(s,8.7,1.5,3.9,2.6); text(s,'自治体面（市の窓口）',8.9,1.65,3.5,0.4,{size:15,bold:true}); text(s,'登録コロニーの状態と期限が一覧になる。申請と報告の副産物として残るので、担い手が代わっても市に情報が残る。届いた申請の不備が減る。',8.9,2.1,3.5,1.9,{size:11.5});
  s.addText([{text:' やらないこと ',options:{fill:{color:RUST},color:WHITE,fontSize:9,bold:true}},{text:'  担い手を増やさない。捕獲しない。説得しない。制度と担い手の間の、時間と引継ぎの摩擦だけを消す。',options:{fontSize:11.5,color:WHITE}}],{x:ML,y:4.5,w:5.6,h:0.9,fontFace:F,isTextBox:true,margin:0,valign:'top',lineSpacingMultiple:1.25});
  s.addText([{text:' 0になるもの ',options:{fill:{color:RUST},color:WHITE,fontSize:9,bold:true}},{text:'  日程逆算、書類、規約適合チェック、期限管理、記録。',options:{fontSize:11.5,color:WHITE,breakLine:true}},{text:' 0にならないもの ',options:{fill:{color:MUTED},color:WHITE,fontSize:9,bold:true}},{text:'  捕獲の腕、深夜の授乳、対面の説得。',options:{fontSize:11.5,color:WHITE}}],{x:6.9,y:4.5,w:5.7,h:0.9,fontFace:F,isTextBox:true,margin:0,valign:'top',lineSpacingMultiple:1.25});
  foot(s,'',6);
}
// 7 なぜAI
{ const s=slide();
  title(s,'要綱は自然言語で公開され、自治体ごとに違う。だから今までは作れず、LLMなら作れる。',{h:0.7});
  text(s,'技術の言葉',ML,1.45,5.8,0.3,{size:11,color:MUTED,bold:true});
  bullets(s,['入力は要綱PDF・様式DOCX・FAQ。構造化されていない。','自治体を変えると条文も様式も変わる。ルールベースなら自治体ごとに再実装。','LLMは条文から「受付日・有効期限・必要人数・必要書類・報告期限」を抽出し、個別の日程に落とし、様式のセル構造を読んで転記する。日付の計算だけはコード側。','自治体プロファイル（要綱一式のフォルダ）を差し替えるだけで別の自治体に対応。規則はコードに1行も書かない。'],ML,1.8,5.8,4.0,12.5);
  text(s,'事業の言葉',6.9,1.45,5.7,0.3,{size:11,color:MUTED,bold:true});
  bullets(s,['全国の協働自治体は298（どうぶつ基金2022年度）。それぞれ要綱が違う。','1自治体あたりの担い手は数十〜数百人。個別開発が成立する規模ではない。','だから誰も作らず、現場は電話とExcelのまま。要綱を読む部分をAIに置くと、初めて1本のシステムで全自治体を扱える。'],6.9,1.8,5.7,2.2,12.5);
  const fx=6.9, fy=4.2;
  box(s,fx,fy,1.35,0.5,'京都市 要綱',null,{size:10.5}); box(s,fx,fy+1.1,1.35,0.5,'高島市 要綱',null,{size:10.5});
  box(s,fx+1.85,fy+0.4,1.35,0.8,'同じエンジン',null,{fill:NAVY,line:NAVY,color:WHITE,size:10.5});
  box(s,fx+3.7,fy-0.1,2.0,0.75,'登録は3年有効\n報告は登録日と同月日から30日以内\n更新は満了日の30日前から',null,{fill:WHITE,line:RUST,size:8.5});
  box(s,fx+3.7,fy+0.95,2.0,0.75,'毎月6日〜末日に申請\n翌々月分のチケット・1か月有効\n写真付き報告、未報告なら次回不可',null,{fill:WHITE,line:RUST,size:8.5});
  [[fx+1.35,fy+0.25,fx+1.85,fy+0.6],[fx+1.35,fy+1.35,fx+1.85,fy+1.0],[fx+3.2,fy+0.6,fx+3.7,fy+0.28],[fx+3.2,fy+1.0,fx+3.7,fy+1.32]].forEach(a=>s.addShape(P.ShapeType.line,{x:Math.min(a[0],a[2]),y:Math.min(a[1],a[3]),w:Math.abs(a[2]-a[0]),h:Math.abs(a[3]-a[1])||0.001,line:{color:MUTED,width:1},flipV:a[3]<a[1]}));
  foot(s,'出典：どうぶつ基金 2022年度実績（個人3,546名／47団体／298行政／約62,128頭）',7);
}
// 8 画面①
{ const s=slide();
  title(s,'開くと「次にやること」が1枚出る。会話で状況を入れると、要綱に照らした不足が返り、様式が埋まって出る。',{h:0.9});
  const lw=6.1; img(s,'next.jpg',ML,1.55,lw); let y=1.55+imgH('next.jpg',lw); cap(s,'何を・いつまでに・様式は何、を1枚で。要綱から抽出した工程と台帳の状態から組み立てる。',ML,y+0.05,lw,0.35);
  y+=0.45; img(s,'rules_s.jpg',ML,y,lw); y+=imgH('rules_s.jpg',lw); cap(s,'京都市要綱に照らした判定。「11頭（10頭以上）のため京都市民3名以上」「周辺地図は別途添付」「登録後に第4号様式」。根拠の条文引用付き。',ML,y+0.05,lw,0.5);
  const rx=7.2, rw=5.4, rh=4.55; s.addImage({path:IMG+'form1.jpg',x:rx,y:1.55,w:rw,h:rh,sizing:{type:'crop',x:0,y:0,w:1215,h:1215*rh/rw}}); s.addShape(P.ShapeType.rect,{x:rx,y:1.55,w:rw,h:rh,line:{color:'D5DBE1',width:0.75},fill:{type:'none'}});
  cap(s,'京都市配布の第1号様式（登録申請書）DOCX に転記した結果。第6号様式（実施計画書）・第4号様式（手術実施申請書）も同様に出る。',rx,1.55+rh+0.05,rw,0.5);
  foot(s,'画面はプロトタイプ（Streamlit）。デモ用の架空コロニー（左京区・11頭・活動者3名）',8);
}
// 9 画面②
{ const s=slide();
  title(s,'市は、届いた申請の不備をなくし、更新が切れそうな地域を先に知る。',{h:0.7});
  const lw=7.0; img(s,'muni_list.jpg',ML,1.45,lw); let y=1.45+imgH('muni_list.jpg',lw); cap(s,'登録コロニー一覧：区／頭数／手術済み頭数／登録日／次回報告期限／更新満了日／状態。状態は要綱の期限ルール（報告は登録日と同月日から30日以内、更新は満了日の30日前から）と報告履歴から計算。',ML,y+0.05,lw,0.55);
  y+=0.65; img(s,'muni_detail.jpg',ML,y,lw); y+=imgH('muni_detail.jpg',lw); cap(s,'各コロニーを開くと、提出済みの様式と報告がそのまま見える。いま提出した申請（K-2026-010）がダミー4件と並び、年次報告を出すと「報告済」に変わる。',ML,y+0.05,lw,0.5);
  card(s,8.1,1.45,4.5,2.8); text(s,'「更新待ち → 期限超過」が見える',8.3,1.6,4.1,0.4,{size:13,bold:true}); text(s,'京都市要綱では、期限までに更新されない登録は職権で抹消できる（第7条3項）。廃止届（第3号様式）には理由欄があるが、届出なしで切れた地域の理由は市に残らない。\n\nこの一覧があると、切れる前に見える。活動中の地域数が「3年横ばい」の中身（終了か脱落か）が初めて分かる。',8.3,2.05,4.1,2.1,{size:11});
  text(s,'引継ぎのために別途入力させるものではない。申請と報告の副産物として市に残る。',8.1,4.4,4.5,0.7,{size:11,color:MUTED});
  foot(s,'画面はプロトタイプ。台帳のダミーは架空。出典：京都市まちねこ活動支援要綱 第7条',9);
}
// 10 結果と指標
{ const s=slide();
  title(s,'受付を逃さず、登録が失効せず、担い手が代わっても途切れない。',{h:0.7});
  const rows=[[{text:'変わること',options:{bold:true,fill:{color:LIGHT}}},{text:'指標',options:{bold:true,fill:{color:LIGHT}}}],['受付を逃さないので、手術が繁殖期に間に合う','申請から手術までの日数'],['報告・更新を落とさない','登録の継続率（職権抹消の減少）'],['担い手が代わっても市に情報が残る','引継ぎ後に活動が継続した地域数'],['市は不備のない申請だけ受ける','センター収容の子猫数（京都市10年評価と同じ系列）']];
  s.addTable(rows,{x:ML,y:1.5,w:CW,colW:[6.2,5.63],fontFace:F,fontSize:13,color:NAVY,border:{type:'solid',color:LINE,pt:0.75},rowH:0.55,margin:0.1,valign:'middle'});
  card(s,ML,4.5,5.75,1.6); text(s,[{text:'測れない指標は置かない。',options:{bold:true}},{text:'「生まれる子猫の数」は測れないので、市が公表しているセンター収容数を使う。事業の効果（収容減・苦情減）をツールの効果として語らない。ツールは事業を速く広く回せるようにするまで。'}],ML+0.2,4.6,5.35,1.4,{size:11});
  card(s,6.85,4.5,5.75,1.6); text(s,[{text:'規則で決まる待ちはツールでは消せない。',options:{bold:true}},{text:'消せるのは、受付を逃す・報告を落とす・書類の不備で戻される、の3つ。高島市の規則では受付を1回逃すと有効月が1か月遅れる（12ページ）。'}],7.05,4.6,5.35,1.4,{size:11});
  foot(s,'',10);
}
// 11 実現の道筋
{ const s=slide();
  title(s,'京都市で立ち上げ、動物病院と苦情窓口から担い手に届ける。',{h:0.7});
  bullets(s,['場所：京都市。要綱・様式・記載例が公開され、10年分の実績があり、市が活動地域数の横ばいを課題として書いている。','払い手：市の既存予算（手術無償化・保護器貸出・助言）の事務コスト。新規予算ではない。','届け方：制度を知らない担い手が既に現れている場所に置く。①動物病院（京都市獣医師会はまちねこ活動をサポートすると明言）②苦情窓口（苦情の裏には餌やりの人がいる）。','段階：京都市1自治体で継続率と日数を測る → 基金型自治体（高島市）にプロファイルを追加 → 協働自治体へ。'],ML,1.5,6.6,4.2,13);
  const fx=8.0, fy=1.6;
  text(s,'プロファイル（要綱一式）を足すだけ。エンジンは共通。',fx,fy,4.6,0.3,{size:10,color:MUTED});
  box(s,fx,fy+2.6,1.45,0.85,'京都市','登録型・実装済',{fill:NAVY,line:NAVY,color:WHITE,subColor:'AAB4BE'});
  box(s,fx+1.6,fy+1.6,1.45,0.85,'高島市','基金チケット型・実装済',{fill:'3B4A5A',line:'3B4A5A',color:WHITE,subColor:'AAB4BE'});
  box(s,fx+3.2,fy+0.6,1.45,0.85,'協働自治体','298（2022年度）',{dash:'dash'});
  arrow(s,fx+1.45,fy+3.0,fx+1.6,fy+3.0,MUTED); arrow(s,fx+3.05,fy+2.0,fx+3.2,fy+2.0,MUTED);
  foot(s,'出典：京都市獣医師会 まちねこページ／京都市10年評価／どうぶつ基金 2022年度実績',11);
}
// 12 展開
{ const s=slide();
  title(s,'自治体プロファイルを差し替えるだけで、要綱で動く制度すべてに同じエンジンが使える。',{h:0.7});
  bullets(s,['このエンジンが読んでいるのは「猫の要綱」ではなく「自治体が自然言語で公開している要綱と様式」。','同じ形の制度は他にもある：住民が申請し、期限があり、報告と更新があり、担い手が無償で属人的なもの。','猫はその中で、効果が実証済みで、担い手が最も薄く、市が障壁を認めた場所。だからここから。','高島市プロファイルで確認済み：同じ入力から「毎月6日〜末日申請・翌々月チケット・写真付き報告・報告しないと次回申請不可」という別の規則と日程が出る。'],ML,1.5,5.4,4.5,12.5);
  const rx=6.5, rw=6.1; img(s,'tk_sim.jpg',rx,1.45,rw); let y=1.45+imgH('tk_sim.jpg',rw); cap(s,'高島市：準備完了日を入れると、受付期間から「最短の申請日 → チケット有効期間 → この受付を逃すと+30日」が出る。受付の値は市HPの記載から抽出し、日付の計算だけコード側。',rx,y+0.05,rw,0.5);
  y+=0.6; img(s,'tk_rules_s.jpg',rx,y,rw); y+=imgH('tk_rules_s.jpg',rw); cap(s,'高島市の資料から抽出した規則に照らした判定。京都市と同じ画面、同じコード。',rx,y+0.05,rw,0.35);
  foot(s,'出典：高島市 環境政策課ページ／どうぶつ基金 チケットFAQ・登録規約',12);
}
// 13 チーム
{ const s=slide(true);
  title(s,'チーム【チーム名】',{h:0.7});
  ['【武蔵】','【神園】','【さくちゃん】','【中田】'].forEach((n,i)=>{ const x=ML+i*3.0; card(s,x,1.5,2.8,1.6); text(s,n,x+0.2,1.65,2.4,0.4,{size:15,bold:true}); text(s,'【役割】',x+0.2,2.1,2.4,0.8,{size:11}); });
  text(s,'プロトタイプ：Python／Streamlit／Anthropic API（Claude）／python-docx。京都市・高島市の2プロファイルで動作。要綱の規則はコードに書かず、資料フォルダから毎回抽出。\n\n現状の限界：当事者ヒアリングは未実施（通過後に京都市医療衛生センター・どうぶつ基金へ）。高島市は市HP本文から抽出しており、交付要綱PDFは未取得。',ML,3.5,CW,1.6,{size:11,color:'AAB4BE'});
  foot(s,'',13);
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
P.writeFile({fileName:'/home/user/VORN/docs/deck/VORN2026_submission.pptx'}).then(f=>console.log('written',f));
