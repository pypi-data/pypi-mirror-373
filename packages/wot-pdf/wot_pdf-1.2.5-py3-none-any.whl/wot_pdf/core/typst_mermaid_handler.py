#!/usr/bin/env python3
"""
🎯 WOT-PDF Typst Mermaid Handler
================================

Dolgoročna rešitev za Mermaid → Typst compatibility.
Pretvarja Mermaid diagrame v SVG slike in ustvari Typst-kompatibilne reference.

Author: WOT-PDF Team
Version: 1.0.0
Compatible with: Typst 0.11+
"""

import re
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import requests
import hashlib
import json

class TypstMermaidHandler:
    """Pametni handler za Mermaid → Typst konverzijo."""
    
    def __init__(self, output_dir: str = "diagrams", use_kroki: bool = True):
        """
        Args:
            output_dir: Mapa za SVG diagrame
            use_kroki: Ali uporabiti Kroki.io server (ne potrebuje Node.js)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_kroki = use_kroki
        self.kroki_url = "https://kroki.io/mermaid/svg"
        
    def extract_mermaid_blocks(self, content: str) -> List[Dict]:
        """Izvleče vse Mermaid bloke iz markdown vsebine."""
        blocks = []
        pattern = r'```mermaid\n(.*?)\n```'
        
        for i, match in enumerate(re.finditer(pattern, content, re.DOTALL)):
            mermaid_code = match.group(1).strip()
            block_id = f"diagram_{i+1}"
            
            # Generate unique filename based on content hash
            hash_obj = hashlib.md5(mermaid_code.encode())
            filename = f"{block_id}_{hash_obj.hexdigest()[:8]}.svg"
            
            blocks.append({
                'id': block_id,
                'code': mermaid_code,
                'filename': filename,
                'start': match.start(),
                'end': match.end(),
                'original': match.group(0)
            })
            
        return blocks
    
    def generate_svg_via_kroki(self, mermaid_code: str, output_path: Path) -> bool:
        """Generiraj SVG preko Kroki.io servisa."""
        try:
            # Kroki sprejema diagram encoding
            import base64
            import zlib
            
            # Encode diagram
            compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
            encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
            
            # Get SVG from Kroki
            kroki_url = f"https://kroki.io/mermaid/svg/{encoded}"
            response = requests.get(kroki_url, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ Generated via Kroki: {output_path.name}")
                return True
            else:
                print(f"❌ Kroki error {response.status_code}: {output_path.name}")
                return False
                
        except Exception as e:
            print(f"❌ Kroki failed for {output_path.name}: {e}")
            return False
    
    def generate_svg_via_mermaid_cli(self, mermaid_code: str, output_path: Path) -> bool:
        """Generiraj SVG preko lokalne mermaid-cli."""
        try:
            # Create temporary mermaid file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp:
                tmp.write(mermaid_code)
                tmp_path = tmp.name
            
            # Run mermaid-cli
            result = subprocess.run([
                'mmdc', '-i', tmp_path, '-o', str(output_path)
            ], capture_output=True, text=True, timeout=60)
            
            # Cleanup
            os.unlink(tmp_path)
            
            if result.returncode == 0:
                print(f"✅ Generated via CLI: {output_path.name}")
                return True
            else:
                print(f"❌ CLI error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout generating {output_path.name}")
            return False
        except Exception as e:
            print(f"❌ CLI failed for {output_path.name}: {e}")
            return False
    
    def create_fallback_svg(self, mermaid_code: str, output_path: Path, diagram_id: str) -> bool:
        """Ustvari fallback SVG z osnovnimi informacijami."""
        try:
            # Simple SVG placeholder
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
  <text x="200" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#495057">
    📊 Mermaid Diagram
  </text>
  <text x="200" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#6c757d">
    {diagram_id.replace('_', ' ').title()}
  </text>
  <text x="200" y="160" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#868e96">
    Generated by WOT-PDF
  </text>
  <text x="200" y="200" text-anchor="middle" font-family="monospace" font-size="10" fill="#adb5bd">
    Lines: {len(mermaid_code.split())}
  </text>
</svg>'''
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"📋 Created fallback: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Fallback failed for {output_path.name}: {e}")
            return False
    
    def process_markdown_for_typst(self, input_file: str, output_file: str = None) -> str:
        """Proces kompletne Markdown → Typst konverzije z Mermaid handling."""
        
        input_path = Path(input_file)
        if not output_file:
            output_file = input_path.stem + "_typst_ready.md"
        
        # Read input
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Mermaid blocks
        mermaid_blocks = self.extract_mermaid_blocks(content)
        
        if not mermaid_blocks:
            print("ℹ️  No Mermaid blocks found")
            return content
        
        print(f"🔍 Found {len(mermaid_blocks)} Mermaid blocks")
        
        # Process each block
        processed_content = content
        for block in reversed(mermaid_blocks):  # Reverse to maintain positions
            svg_path = self.output_dir / block['filename']
            
            # Try to generate SVG
            success = False
            
            if self.use_kroki:
                success = self.generate_svg_via_kroki(block['code'], svg_path)
            
            if not success:
                # Try mermaid-cli as backup
                success = self.generate_svg_via_mermaid_cli(block['code'], svg_path)
            
            if not success:
                # Create fallback
                success = self.create_fallback_svg(block['code'], svg_path, block['id'])
            
            if success:
                # Replace Mermaid block with Typst image reference
                typst_ref = f'#figure(\n  image("{self.output_dir.name}/{block["filename"]}"),\n  caption: [Architecture Diagram: {block["id"].replace("_", " ").title()}]\n)'
                
                # Replace in content
                processed_content = processed_content.replace(block['original'], typst_ref)
                
                print(f"🔄 Replaced {block['id']} → {block['filename']}")
        
        # Save processed content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"✅ Typst-ready file: {output_file}")
        return processed_content

def main():
    """CLI interface za testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python typst_mermaid_handler.py input.md [output.md]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    handler = TypstMermaidHandler()
    handler.process_markdown_for_typst(input_file, output_file)

if __name__ == "__main__":
    main()
