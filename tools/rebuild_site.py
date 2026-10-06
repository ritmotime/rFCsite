from pathlib import Path
import json,re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from bs4 import BeautifulSoup
import tinycss2
site=Path(__file__).resolve().parents[1]
release=json.loads((site/'WEB-RELEASE.json').read_text())['release']
if not re.fullmatch(r'[A-Za-z0-9._-]+', release):
 raise ValueError('WEB-RELEASE.json release must contain only letters, numbers, dots, underscores or hyphens')

def version_url(value):
 parts=urlsplit(value)
 query=[(k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True) if k!='v']
 return urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(query+[('v',release)]),parts.fragment))

old=(site/'index.html').read_text()
nav=json.loads(re.search(r'window.RFC_NAV=(.*?);</script>',old,re.S).group(1))
# Keep historical deep-link IDs while consolidating alignment into one guide.
for cat in nav:
 if cat['id']=='oar-kit':
  cat['pages']=[{'id':'oar-kit','title':'Assembly & Mounting','file':'instructions.html'}, {'id':'connect-oar-sensors','title':'Sensor Direction','file':'oar-sensor-alignment-guide.html'}, {'id':'oar-kit-videos','title':'Kit Videos','file':'oar_kit_videos.html'}]
 if cat['id']=='mobile-app':
  cat['title']='iOS App'
  cat['pages']=[p for p in cat['pages'] if p['id'] not in ('android-recording','ios-connect','ios-alignment')]
  cat['pages'].insert(1,{'id':'ios-connect','title':'Connect in iOS','file':'connecting_oar_sensors.html'})
  cat['pages'].insert(2,{'id':'ios-alignment','title':'Align & Record','file':'ios_alignment.html'})
# Each platform has a complete recording path; analysis is shared after upload.
android={'id':'android','title':'Android','pages':[
 {'id':'android-recording','title':'Oar Sensors & Alignment','file':'android_recording.html'},
 {'id':'android-phone','title':'Phone Motion & GPS','file':'android_phone_recording.html'},
]}
nav=[cat for cat in nav if cat['id']!='android']
nav.insert(next(i for i,cat in enumerate(nav) if cat['id']=='mobile-app')+1,android)
# Make Rowing Physics directly visible while preserving its historical page ID.
physics={'id':'force-curve-physics','title':'Rowing Physics','file':'force_curve_physics.html'}
for cat in nav:
 if cat['id']=='data-metrics': cat['pages']=[p for p in cat['pages'] if p['id']!='force-curve-physics']
if not any(c['id']=='rowing-physics' for c in nav):
 pos=next(i for i,c in enumerate(nav) if c['id']=='data-metrics')+1
 nav.insert(pos,{'id':'rowing-physics','title':'Rowing Physics','pages':[physics]})
# Report and boat-motion guides share the Cloud Analysis section.
for cat in nav:
 if cat['id']=='cloud-analysis':
  cat['pages']=[
   {'id':'cloud-analysis','title':'Overview','file':'cloud_analysis.html'},
   {'id':'report-guide','title':'Explore a report','file':'report_guide.html'},
   {'id':'boat-motion','title':'Boat motion & replay','file':'boat_motion.html'},
  ]
# Apply shared appearance to all real help pages, preserving their body and logic.
for p in site.glob('*.html'):
 if p.name in ('index.html','index_old.html','example_workout.html','example_workout_previous.html'): continue
 s=BeautifulSoup(p.read_text().replace('oar lock', 'oarlock').replace('Oar lock', 'Oarlock'), 'html.parser')
 if not s.head: continue
 s.html['data-rfc-accent']='teal'
 for brand in s.select('.wordmark'):
  if not brand.select_one('.trademark'):
   mark=s.new_tag('sup',attrs={'class':'trademark'});mark.string='™';brand.append(mark)
 if s.title and '™' not in s.title.get_text():
  s.title.string=s.title.get_text().replace('RitmoForceCurve','ritmoForceCurve™')
 for link in s.select('link[rel="stylesheet"]'):
  href=link.get('href','')
  if href and not urlsplit(href).scheme and not urlsplit(href).netloc: link['href']=version_url(href)
 for script in s.select('script[src]'):
  src=script['src']
  if not urlsplit(src).scheme and not urlsplit(src).netloc: script['src']=version_url(src)
 if not s.select_one('script[src^="site-theme.js"]'):
  script=s.new_tag('script',src=version_url('site-theme.js'));s.head.insert(0,script)
 theme=s.find('meta',attrs={'name':'theme-color'})
 if theme: theme['content']='#242a32'
 for node in s.select('[src], [poster], a[href]'):
  for attr in ('src','poster','href'):
   value=node.get(attr,'')
   parts=urlsplit(value)
   if not parts.scheme and not parts.netloc and (parts.path.startswith('assets/') or parts.path=='example_workout.html'):
    node[attr]=version_url(value)
 for right in s.select('.page-topnav > div'): right.decompose()
 for a in s.select('.page-topnav a'):
  if a.get('href','').startswith('android_recording.html'): a.string='Align & record'
 p.write_text(str(s))

def scoped_css(css,scope):
 out=[]
 for rule in tinycss2.parse_stylesheet(css,skip_comments=True,skip_whitespace=True):
  if rule.type=='qualified-rule':
   # Top-level commas separate selectors; commas inside :is() or attribute
   # selectors belong to the same selector and must be preserved.
   groups=[[]]
   for token in rule.prelude:
    if token.type=='literal' and token.value==',': groups.append([])
    else: groups[-1].append(token)
   sels=[tinycss2.serialize(group).strip() for group in groups]
   sels=[f'{scope} {x.strip()}' for x in sels if x.strip() not in ['html','body',':root','*']]
   if sels: out.append(','.join(sels)+'{'+tinycss2.serialize(rule.content)+'}')
  elif rule.type=='at-rule' and rule.content and rule.lower_at_keyword in ['media','supports']:
   out.append('@'+rule.at_keyword+' '+tinycss2.serialize(rule.prelude)+'{'+scoped_css(tinycss2.serialize(rule.content),scope)+'}')
 return '\n'.join(out)

panels=[];styles=[];extras=set()
for cat in nav:
 for page in cat['pages']:
  s=BeautifulSoup((site/page['file']).read_text(),'html.parser')
  for st in s.head.find_all('style'): styles.append(scoped_css(st.get_text(),'#page-'+page['id']))
  for link in s.head.select('link[rel="stylesheet"]'):
   href=link.get('href','')
   if href and not href.startswith('site.css'): extras.add(href)
  body=s.body
  for n in body.select('.page-topnav'): n.decompose()
  for m in body.find_all('main'): m.name='div'
  content=''.join(str(x) for x in body.contents)
  hidden='' if page['id']=='welcome' else ' hidden'
  panels.append(f'<section class="rfc-page-panel" id="page-{page["id"]}" data-page="{page["id"]}"{hidden}>{content}</section>')
(site/'scoped-pages.css').write_text('\n'.join(styles))
links=''.join(f'<link rel="stylesheet" href="{href}">' for href in sorted(extras))
menu='\n'.join(f'<a href="{c["pages"][0]["file"]}" data-category="{c["id"]}">{c["title"]}</a>' for c in nav)
html='''<!doctype html><html lang="en" data-rfc-accent="teal"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#242a32"><meta name="description" content="Understand oar motion, rowing effort and every part of your stroke. iOS live feedback, Android recording and interactive workout analysis."><title>ritmoForceCurve™</title><script src="site-theme.js?v='''+release+'''"></script><link rel="stylesheet" href="site.css?v='''+release+'''"><link rel="stylesheet" href="scoped-pages.css?v='''+release+'''">'''+links+'''</head><body><a class="skip-link" href="#content">Skip to content</a><div class="site-shell"><header class="page-topnav"><a class="wordmark" href="index.html">ritmo<span>ForceCurve</span><sup class="trademark">™</sup></a></header><nav class="site-nav" aria-label="Main navigation"><div class="fc-top-buttons">'''+menu+'''</div><div class="fc-sub-buttons" id="subnav" aria-label="Section navigation" hidden></div></nav><main id="content">'''+ '\n'.join(panels)+'''</main></div><script>window.RFC_NAV='''+json.dumps(nav)+''';</script><script src="site-nav.js?v='''+release+'''"></script></body></html>'''
(site/'index.html').write_text(html)
# Retired entry point must not keep presenting obsolete setup instructions.
(site/'index_old.html').write_text('<!doctype html><html lang="en" data-rfc-accent="teal"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=index.html"><title>ritmoForceCurve™</title></head><body><p><a href="index.html">Open the current RitmoForceCurve website</a>.</p></body></html>')
print('Built',len(panels),'panels; stylesheets:',sorted(extras))
