#!/usr/bin/env python3
"""
Systematic test to find the minimum amount of reward shaping needed for mutual cooperation
"""

import numpy as np
import torch
import logging
import os

from cooperative_mappo_trainer import CooperativeMAPPOTrainer, create_cooperative_training_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_minimum_reward_shaping():
    
    # Test different bonus levels systematically
    bonus_levels = [0.625]
    penalty_levels = [0.5, 1, 1.5]

    results = []
    
    # Test with different bonus levels
    for bonus in bonus_levels:
        for penalty in penalty_levels:
            logging.info(f"Testing: Bonus={bonus:.1f}")
            
            # Set random seeds
            np.random.seed(42)
            torch.manual_seed(42)
            
            # Create configuration
            config = create_cooperative_training_config()
            config['cooperation_bonus'] = bonus
            config['defection_penalty'] = penalty
            config['total_timesteps'] = 1500
            config['eval_interval'] = 500
            config['save_interval'] = 1500
            
            # Update save directory
            config['save_dir'] = os.path.join(config['save_dir'], f"min_reward_test_b{bonus},_penalty_{penalty}")
            
            try:
                # Initialize trainer
                trainer = CooperativeMAPPOTrainer(config)
                
                # Train
                logging.info("Training...")
                trainer.train()
                
                # Evaluate
                eval_results = trainer.evaluate(num_episodes=5)
                
                cooperation_rate = eval_results['eval_cooperation_rate']
                mutual_cooperation_rate = eval_results['eval_mutual_cooperation_rate']
                reward_mean = eval_results['eval_reward_mean']
                
                logging.info(f"Results:")
                logging.info(f"  Cooperation Rate: {cooperation_rate:.2%}")
                logging.info(f"  Mutual Cooperation Rate: {mutual_cooperation_rate:.2%}")
                logging.info(f"  Reward Mean: {reward_mean:.3f}")
                
                # Check if target achieved
                target_achieved = cooperation_rate >= 0.65
                
                if target_achieved:
                    logging.info(f"TARGET ACHIEVED!")
                else:
                    logging.info(f"Target NOT achieved")
                
                result = {
                    'bonus': bonus,
                    'cooperation_rate': cooperation_rate,
                    'mutual_cooperation_rate': mutual_cooperation_rate,
                    'reward_mean': reward_mean,
                    'target_achieved': target_achieved
                }
                
                results.append(result)

            except Exception as e:
                logging.error(f"Error testing bonus={bonus}: {str(e)}")
                result = {
                    'bonus': bonus,
                    'error': str(e)
                }
                results.append(result)

    valid_results = [r for r in results if 'error' not in r]
    successful_results = [r for r in valid_results if r['target_achieved']]
    
    if successful_results:
        logging.info(f"SUCCESSFUL CONFIGURATIONS ({len(successful_results)}):")
        
        # Sort by bonus amount to find minimum
        successful_results.sort(key=lambda x: x['bonus'])
        
        for result in successful_results:
            logging.info(f"Bonus={result['bonus']:>6.1f}: "
                        f"Coop={result['cooperation_rate']:>6.2%}, "
                        f"Mutual={result['mutual_cooperation_rate']:>6.2%}")
        
        # Find minimum successful bonus
        min_successful_bonus = min(r['bonus'] for r in successful_results)
        
        logging.info(f"\nMINIMUM MUTUAL COOPERATION BONUS NEEDED:")
        logging.info(f"Cooperation Bonus: {min_successful_bonus:.1f}")
        
        # Find the most efficient configuration (lowest bonus that achieves target)
        most_efficient = min(successful_results, key=lambda x: x['bonus'])
        logging.info(f"\nMOST EFFICIENT CONFIGURATION:")
        logging.info(f"Bonus: {most_efficient['bonus']:.1f}")
        logging.info(f"Cooperation Rate: {most_efficient['cooperation_rate']:.2%}")
        logging.info(f"Mutual Cooperation Rate: {most_efficient['mutual_cooperation_rate']:.2%}")
        
    else:
        logging.info(f"NO SUCCESSFUL CONFIGURATIONS")
    
    # Summary table
    logging.info(f"\n{'='*80}")
    logging.info("SUMMARY TABLE (Bonus | Cooperation | Mutual | Target)")
    logging.info(f"{'='*80}")
    
    for result in valid_results:
        if 'error' not in result:
            status = "Reached" if result['target_achieved'] else "No"
            logging.info(f"{result['bonus']:>6.3f} | "
                        f"{result['cooperation_rate']:>11.2%} | "
                        f"{result['mutual_cooperation_rate']:>6.2%} | {status}")
    
    return results

if __name__ == "__main__":
    test_minimum_reward_shaping()
