#!/usr/bin/env python3

import argparse
import csv
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from datetime import datetime
import logging

class ICABatchProcessor:
    def __init__(self, project_name: str, max_concurrent: int = 5):
        self.project_name = project_name
        self.max_concurrent = max_concurrent
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ica_batch')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('ica_batch.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger

    def process_sample(self, sample: Dict) -> Dict:
        """Process a single sample"""
        try:
            # Upload data
            upload_cmd = [
                'python', 'ica_cli_upload.py',
                sample['data_folder'], self.project_name,
                '--folder-name', sample['sample_id']
            ]
            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Upload failed: {result.stderr}")

            # Generate parameters
            params = self._generate_params(sample)
            params_file = f"{sample['sample_id']}_params.json"
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=4)

            # Run pipeline
            pipeline_cmd = [
                'python', 'ica_cli_workflow.py',
                sample['data_folder'], self.project_name,
                sample['pipeline'], f"./results/{sample['sample_id']}",
                '--params-file', params_file
            ]
            result = subprocess.run(pipeline_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Pipeline failed: {result.stderr}")

            return {
                'sample_id': sample['sample_id'],
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error processing {sample['sample_id']}: {e}")
            return {
                'sample_id': sample['sample_id'],
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _generate_params(self, sample: Dict) -> Dict:
        """Generate pipeline parameters based on sample metadata"""
        base_params = {
            'sample-id': sample['sample_id'],
            'reference-tar': f"/reference-data/{sample['reference']}/{sample['reference']}.fa",
            'output-directory': '/output'
        }

        # Add pipeline-specific parameters
        if sample['pipeline'] == 'dragen-germline':
            base_params.update({
                'enable-map-align': True,
                'enable-sort': True,
                'enable-duplicate-marking': True,
                'enable-variant-caller': True
            })
        elif sample['pipeline'] == 'dragen-rna':
            base_params.update({
                'enable-rna': True,
                'enable-rna-quantification': True,
                'annotation-file': f"/reference-data/{sample['reference']}/genes.gtf"
            })
        elif sample['pipeline'] == 'dragen-enrichment':
            base_params.update({
                'enable-map-align': True,
                'enable-variant-caller': True,
                'vc-target-bed': sample.get('target_bed'),
                'vc-target-bed-padding': 100
            })

        # Add any custom parameters from sample metadata
        if 'custom_params' in sample:
            base_params.update(sample['custom_params'])

        return base_params

    def process_batch(self, sample_sheet: str) -> List[Dict]:
        """Process multiple samples in parallel"""
        # Read sample sheet
        with open(sample_sheet) as f:
            if sample_sheet.endswith('.csv'):
                samples = list(csv.DictReader(f))
            else:
                samples = yaml.safe_load(f)

        results = []
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_sample = {
                executor.submit(self.process_sample, sample): sample
                for sample in samples
            }
            
            for future in future_to_sample:
                result = future.result()
                results.append(result)
                self.logger.info(
                    f"Sample {result['sample_id']} {result['status']}"
                )

        # Generate summary report
        summary = {
            'total_samples': len(samples),
            'completed': len([r for r in results if r['status'] == 'completed']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'timestamp': datetime.now().isoformat()
        }

        # Save results and summary
        output_dir = Path('batch_results')
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / 'results.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        with open(output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=4)

        return results

def main():
    parser = argparse.ArgumentParser(
        description='Process multiple ICA samples in batch'
    )
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('sample_sheet',
                       help='Path to sample sheet (CSV or YAML)')
    parser.add_argument('--max-concurrent', type=int, default=5,
                       help='Maximum number of concurrent processes')
    
    args = parser.parse_args()
    processor = ICABatchProcessor(args.project_name, args.max_concurrent)
    processor.process_batch(args.sample_sheet)

if __name__ == '__main__':
    main()
