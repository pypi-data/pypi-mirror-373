from lognflow.plt_utils import plt, np, plt_imhist
from lognflow import printv

print(f'code_block_id : ', code_block_id)

if code_block_id == 'init':
    print('block name: block init')
    img = np.random.randn(20, 20)
    img[30:50, 30:50] += 10
    plt_imhist(img); plt.show()

if code_block_id == 'double above 50':
    print('block name: double above 50')    
    img[img > 50] *= img[img > 50]
    plt_imhist(img); plt.show()

if code_block_id == 3.0:
    print('block name: 3.0')    
    img[img < 50] = np.exp(-img[img < 50])
    plt_imhist(img); plt.show() 

if code_block_id == 3:
    print('block name: Oh no, another 3')    
    img[img < 50] = np.exp(-img[img < 50])
    plt_imhist(img); plt.show() 

if code_block_id == 2:
    print('block name: 2')    
    img[img < 50] = np.exp(-img[img < 50])
    plt_imhist(img); plt.show() 

if code_block_id == 4.5:
    print('block name: 4.5')    
    img += np.random.randn(100, 100)
    plt_imhist(img); plt.show() 
    
if code_block_id == 'final':
    print('final')    
    img = np.exp(-img)
    plt_imhist(img); plt.show() 
    
printv(img)