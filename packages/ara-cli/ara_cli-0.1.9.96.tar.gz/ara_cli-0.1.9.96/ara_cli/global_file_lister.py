import os
import fnmatch
from typing import List, Dict, Any

# Ağaç yapımız için bir tip tanımı yapalım
DirTree = Dict[str, Any]

def _build_tree(root_path: str, patterns: List[str]) -> DirTree:
    """Belirtilen yoldaki dizin yapısını temsil eden iç içe bir sözlük oluşturur."""
    tree: DirTree = {'files': [], 'dirs': {}}
    try:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                subtree = _build_tree(item_path, patterns)
                # Sadece içinde dosya olan veya dosyası olan alt klasörleri ekle
                if subtree['files'] or subtree['dirs']:
                    tree['dirs'][item] = subtree
            elif os.path.isfile(item_path):
                # Dosyanın verilen desenlerden herhangi biriyle eşleşip eşleşmediğini kontrol et
                if any(fnmatch.fnmatch(item, pattern) for pattern in patterns):
                    tree['files'].append(item)
    except OSError as e:
        print(f"Warning: Could not access path {root_path}: {e}")
    return tree

def _write_tree_to_markdown(md_file, tree: DirTree, level: int):
    """Ağaç veri yapısını markdown formatında dosyaya yazar."""
    # Dosyaları girintili olarak yaz
    indent = '    ' * level
    for filename in sorted(tree['files']):
        md_file.write(f"{indent}- [] {filename}\n")
    
    # Alt dizinler için başlık oluştur ve recursive olarak devam et
    for dirname, subtree in sorted(tree['dirs'].items()):
        # Alt başlıklar için girinti yok, sadece başlık seviyesi artıyor
        md_file.write(f"{'    ' * (level -1)}{'#' * (level + 1)} {dirname}\n")
        _write_tree_to_markdown(md_file, subtree, level + 1)

def generate_global_markdown_listing(directories: List[str], file_patterns: List[str], output_file: str):
    """
    Global dizinler için hiyerarşik bir markdown dosya listesi oluşturur.
    En üst başlık olarak mutlak yolu kullanır, alt öğeler için göreceli isimler kullanır.
    """
    with open(output_file, 'w', encoding='utf-8') as md_file:
        for directory in directories:
            abs_dir = os.path.abspath(directory)
            
            if not os.path.isdir(abs_dir):
                print(f"Warning: Global directory not found: {abs_dir}")
                md_file.write(f"# {directory}\n")
                md_file.write(f"    - !! UYARI: Dizin bulunamadı: {abs_dir}\n\n")
                continue

            tree = _build_tree(abs_dir, file_patterns)
            
            # Sadece ağaç boş değilse yaz
            if tree['files'] or tree['dirs']:
                md_file.write(f"# {abs_dir}\n")
                _write_tree_to_markdown(md_file, tree, 1)
                md_file.write("\n")