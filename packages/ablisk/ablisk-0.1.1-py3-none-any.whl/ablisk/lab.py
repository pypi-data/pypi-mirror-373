# Dependencies
import scipy.stats as scs
import numpy as np
import plotly.graph_objects as go
import pandas as pd


# A class for A/B tests
class ABLisk:
    
    # Initializing the class
    def __init__(self, bcr: float, mde: float, alpha: float = .05, power: float = .8, is_absolute_variation: bool = True, is_two_tailed: bool = True):
        
        '''
        Parameters
        ----------
        - bcr: the Baseline Conversion Rate.
        - mde: the Minimum Detectable Effect (or practical significance).
        - alpha: the Significance level of the experiment (default: 0.05).
        - power: statistical power — measures the probability that the test will
          reject the null hypothesis if the treatment really has an effect 
          (default: 0.8).
        - is_absolute_variation: whether the diffrence between the two groups is
          absolute or relative (default: True)
        -  is_two_tailed: for deciding between a two or a one-tailed test (default: True)
        '''
        
        # BCR value condition
        if isinstance(bcr, (int, float)) and ((bcr < .0) or (bcr > 1.0)):
            raise ValueError('Baseline Conversion Rate (bcr) spans from 0 and 1.')
        elif not isinstance(bcr, (int, float)):
            raise TypeError(f'Baseline Conversion Rate (bcr) must be a number! "{bcr}" was inserted instead.')

        # MDE value condition 
        if isinstance(mde, (int, float)) and ((mde <= .0) or (mde > 1.0)):
            raise ValueError('Minimum Detectable Effect must be greater than 0 or equal to 1!')
        elif not isinstance(mde, (int, float)):
            raise TypeError(f'Minimum Detectable Effect must be a number! "{mde}" was inserted instead.')
         
        # Significance Level and Power entries condition
        if (not isinstance(alpha, (int, float))) or ((alpha < 0) or (alpha > 1)):
            raise ValueError(f'Significance level must be between 0 and 1! Received "{alpha}".')
        if (not isinstance(power, (int, float))) or ((power < 0) or (power > 1)):
            raise ValueError(f'Power must range between 0 and 1! Received "{power}".')
                
        # Attributes
        self.bcr = bcr
        self.effect_size = mde if is_absolute_variation else bcr * mde
        self.tail = alpha/2 if is_two_tailed else alpha
        self.power = power
       
        
    # Evan Miller Sample Size Calculator   
    def evan_miller_sample_size(self) -> int:
        
        '''
        A method for retrieving the required sample size using Evan Miller's 
        methodology.
        '''  
        
        try:   
            # Setting the variation type    
            p2 = self.bcr + self.effect_size
            q1, q2 = 1 - self.bcr, 1 - p2 
        
            # Z-scores for significance level and power
            z_alpha = scs.norm.ppf(1 - self.tail)    
            z_power = scs.norm.ppf(self.power)
            
            # Calculating the standard deviations
            std1 = np.sqrt(2 * self.bcr * q1)
            std2 = np.sqrt(self.bcr * q1 + p2 * q2)
            
            # Computing the sample size per group
            sample_size = pow(
                (z_alpha * std1 + z_power * std2) / self.effect_size, 2
            )    
            return round(sample_size)
        except:
            print('Are you sure about BCR and MDE values?')

    
    # A method for experiment results summary
    def get_experiment_results(self, n_ctrl: int, p_ctrl: float, n_trmt: int, p_trmt: float, plot_ = None):  
        """
        Method for retrieving the experiment results.
        
        Parameters
        ----------
        - n_ctrl: the sample size of the control group.
        - n_trmt: the size of the treatment group.
        - p_ctrl: the proportion of conversion in the control group.
        - p_trmt: the proportion of conversion in the treatment group.
        - plot_type (default: 'KDE'): parameter for deciding whether to plot 
          KDEs or Confidence Intervals for supporting the final decision.
        """
        
        # Proportions input conditions
        if isinstance(p_ctrl, (int, float)) and ((p_ctrl < .0) or (p_ctrl > 1.0)):
            raise ValueError('Proportion of conversion in the "Control" group spans from 0 and 1.')
        elif not isinstance(p_ctrl, (int, float)):
            raise TypeError(f'Proportion for "Control" group must be a number! "{p_ctrl}" was inserted instead.')
        if isinstance(p_trmt, (int, float)) and ((p_trmt < .0) or (p_trmt > 1.0)):
            raise ValueError('Proportion of conversion in the "Treatment" group spans from 0 and 1.')
        elif not isinstance(p_trmt, (int, float)):
            raise TypeError(f'Proportion for "Treatment" group must be a number! "{p_trmt}" was inserted instead.')
            
        # Sample size conditions
        if not(isinstance(n_ctrl, int) and (n_ctrl > 0)):
            raise ValueError(f'Sample size of "Control" group must be a positive number. "{n_ctrl}" was inserted instead.')
        if not(isinstance(n_trmt, int) and (n_trmt > 0)):
            raise ValueError(f'Sample size of "Treatment" group must be a positive number. "{n_trmt}" was inserted instead.')
        
        # Computing the pooled Standard Error
        pooled_p = (n_ctrl * p_ctrl + n_trmt * p_trmt) / (n_ctrl + n_trmt)
        pooled_q = 1 - pooled_p
        pooled_se = np.sqrt(pooled_p * pooled_q * (1 / n_ctrl + 1 / n_trmt))        
        
        # Estimated difference between the two groups and its margin of error
        d_hat = p_trmt - p_ctrl
        norm_trmt = scs.norm(d_hat, pooled_se)
        d_hat_min, d_hat_max = norm_trmt.ppf(self.tail), norm_trmt.ppf(1 - self.tail)
        d_hat_ci = abs(d_hat - d_hat_min)
       
        # Setting the confidence intervals for retaining the null hypothesis
        norm_ctrl = scs.norm(0, pooled_se)
        lower_bound, upper_bound = norm_ctrl.ppf(self.tail), norm_ctrl.ppf(1 - self.tail)
        
        # Plotting options
        if plot_ is not None:
            x_trmt = np.linspace(d_hat - pooled_se * 5, d_hat + pooled_se * 5, int(n_trmt))
            y_trmt = norm_trmt.pdf(x_trmt)
            x_ctrl = np.linspace(- pooled_se * 5, pooled_se * 5, int(n_ctrl))
            y_ctrl = norm_ctrl.pdf(x_ctrl)
            
            # KDE Plot
            if plot_ == 'KDE':
                fig = go.Figure()
            
                # Control KDE
                fig.add_trace(go.Scatter(
                    x = x_ctrl,
                    y = y_ctrl,
                    mode = 'lines',
                    line = dict(color = 'red', dash = 'dot'),
                    name = 'Control'
                ))
                fig.add_trace(go.Scatter(
                    x = x_ctrl,
                    y = y_ctrl,
                    fill = 'tozeroy',
                    mode = 'none',
                    fillcolor = 'rgba(255,0,0,0.25)',
                    name = 'Control Area',
                    showlegend = False
                ))
            
                # Treatment KDE
                fig.add_trace(go.Scatter(
                    x = x_trmt,
                    y = y_trmt,
                    mode ='lines',
                    line = dict(color = 'cyan', dash = 'dot'),
                    name = 'Treatment'
                ))
                fig.add_trace(go.Scatter(
                    x = x_trmt,
                    y = y_trmt,
                    fill = 'tozeroy',
                    mode = 'none',
                    fillcolor = 'rgba(0,255,255,0.25)',
                    name = 'Treatment Area',
                    showlegend = False
                ))
            
                # MDE line
                fig.add_trace(go.Scatter(
                    x = [self.effect_size, self.effect_size],
                    y = [0, max(max(y_trmt), max(y_ctrl))],
                    mode = 'lines',
                    line = dict(color = '#04ef62', dash = 'dot'),
                    name = 'MDE'
                ))
            
                # Layout adjustments
                fig.update_layout(
                    title = dict(text = 'Experiment Results'),
                    yaxis = dict(title = '', showticklabels = False),
                    xaxis = dict(title = ''),
                    autosize = True, 
                    margin=dict(l = 50, r = 50, t = 50, b = 50)
                )
                
            
            elif plot_ == 'Confidence Intervals':
                # Error bars and effects
                fig = go.Figure()
            
                # Control Error Bar
                fig.add_trace(go.Scatter(
                    x = [0],
                    y = [5],
                    error_x = dict(type = 'data', symmetric = True, array = [lower_bound, 0, upper_bound]),
                    mode = 'markers',
                    marker = dict(color = 'red', size = 10),
                    name = 'Control'
                ))
            
                # Treatment Error Bar
                fig.add_trace(go.Scatter(
                    x = [d_hat],
                    y = [7],
                    error_x = dict(type = 'data', symmetric = True, array = [d_hat_ci, d_hat, d_hat_ci]),
                    mode = 'markers',
                    marker = dict(color = 'cyan', size = 10),
                    name = 'Treatment'
                ))
            
                # MDE lines
                fig.add_trace(go.Scatter(
                    x = [-self.effect_size, -self.effect_size],
                    y = [3, 9],
                    mode = 'lines',
                    line = dict(color = '#04ef62', dash = 'dot'),
                    name = '-MDE',
                    showlegend = False
                ))
                fig.add_trace(go.Scatter(
                    x = [self.effect_size, self.effect_size],
                    y = [3, 9],
                    mode = 'lines',
                    line = dict(color = '#04ef62', dash = 'dot'),
                    name='MDE',
                    showlegend = False
                ))
            
                # Text annotations
                fig.add_trace(go.Scatter(
                    x = [self.effect_size * 1.25],
                    y = [2.5],
                    mode = 'text',
                    text = 'MDE',
                    textposition = 'top center',
                    showlegend = False
                ))
                fig.add_trace(go.Scatter(
                    x = [-self.effect_size * 1.25],
                    y = [2.5],
                    mode = 'text',
                    text = '-MDE',
                    textposition = 'top center',
                    showlegend = False,
                    
                ))
            
                # Layout adjustments
                fig.update_layout(
                    title = dict(text = 'Experiment Results'),
                    xaxis = dict(title = ''),
                    yaxis = dict(title = '', showticklabels = False),
                    showlegend = True,
                    autosize = True, 
                    margin=dict(l = 50, r = 50, t = 50, b = 50)
                )
            
            # Display the plot
            return fig
        else:
            results = d_hat_min, d_hat, d_hat_max, d_hat - self.effect_size
            idx = ['Min. Difference', 'Estimated Difference', 'Max. Difference', 'Lift/Drop']
            results_df = pd.DataFrame(
                results, columns = [''], index = idx
                ).round(2)

            # Setting recommendations based on experiment results
            if d_hat_min >= self.effect_size:
                recommendation = 'Given that the Minimum Estimated Difference is greater than or equal to the Minimum Detectable Effect, it is recommended to launch the alternative version!'
            elif d_hat_max <= self.effect_size:
                recommendation = 'Since the Maximum Estimated Difference is lower than or equal to the Minimum Detectable Effect, it is then recommended to keep the current version!'
            else:
                recommendation = 'There might not have enough Power to draw any conclusion about the experiment results. Thus, it is recommended to conduct some additional tests.'
            line1 = 'Results and Recomendation\n==========================\n[1] Summary:\n'
            line3 = f'\n\n[2] Recommendation:\n{recommendation}'
            line4 = '\n\n\n\n*Note: This recommendation does not assume that you have designed your experiment correctly.'
            rec_and_sum = line3 + line4            
            print(line1, results_df, rec_and_sum)