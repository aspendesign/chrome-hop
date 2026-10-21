"""Original geometric icon, rendered without external art or trademark assets."""
from pathlib import Path
from PIL import Image, ImageDraw
from run import ROOT

def render(size):
    scale=4
    im=Image.new('RGBA',(128*scale,128*scale),(0,0,0,0))
    d=ImageDraw.Draw(im)
    def box(coords,fill,r=0):
        coords=tuple(int(x*scale) for x in coords)
        if r: d.rounded_rectangle(coords,radius=r*scale,fill=fill)
        else:d.rectangle(coords,fill=fill)
    box((4,4,124,124),'#163b2e',28)
    box((24,32,72,91),'#b5cfb5',10)
    box((32,40,64,83),'#163b2e',4)
    box((57,44,105,103),'#f3ce70',10)
    box((65,52,97,95),'#163b2e',4)
    # The rising arrow bridges the two browser windows.
    d.line([(x*scale,y*scale) for x,y in [(42,75),(82,35),(98,35)]],fill='#ffffff',width=9*scale,joint='curve')
    d.line([(83*scale,21*scale),(99*scale,35*scale),(85*scale,50*scale)],fill='#ffffff',width=9*scale,joint='curve')
    return im.resize((size,size),Image.Resampling.LANCZOS)

if __name__=='__main__':
    target=ROOT/'extension/icons';target.mkdir(parents=True,exist_ok=True)
    assets=ROOT/'assets';assets.mkdir(exist_ok=True)
    for s in (16,32,48,96,128):render(s).save(target/f'hop-{s}.png',optimize=True)
    render(512).save(assets/'chrome-hop-512.png',optimize=True)
    render(256).save(assets/'chrome-hop.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    (assets/'chrome-hop.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><rect x="4" y="4" width="120" height="120" rx="28" fill="#163b2e"/><rect x="24" y="32" width="48" height="59" rx="10" fill="#b5cfb5"/><rect x="32" y="40" width="32" height="43" rx="4" fill="#163b2e"/><rect x="57" y="44" width="48" height="59" rx="10" fill="#f3ce70"/><rect x="65" y="52" width="32" height="43" rx="4" fill="#163b2e"/><path d="M42 75 82 35H98M83 21 99 35 85 50" fill="none" stroke="white" stroke-width="9" stroke-linejoin="round"/></svg>''')
    print('Original icons generated: 16–512px, SVG and ICO.')
