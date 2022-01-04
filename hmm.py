

from __future__ import print_function
import json
import numpy as np


class HMM:

    def __init__(self, pi, A, B, obs_dict, state_dict):
        """
        - pi: (1*num_state) A numpy array of initial probabilities. pi[i] = P(Z_1 = s_i)
        - A: (num_state*num_state) A numpy array of transition probabilities. A[i, j] = P(Z_t = s_j|Z_{t-1} = s_i)
        - B: (num_state*num_obs_symbol) A numpy array of observation probabilities. B[i, k] = P(X_t = o_k| Z_t = s_i)
        - obs_dict: A dictionary mapping each observation symbol to its index 
        - state_dict: A dictionary mapping each state to its index
        """
        self.pi = pi
        self.A = A
        self.B = B
        self.obs_dict = obs_dict
        self.state_dict = state_dict

    def forward(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - alpha: (num_state*L) A numpy array where alpha[i, t-1] = P(Z_t = s_i, X_{1:t}=x_{1:t})
                 (note that this is alpha[i, t-1] instead of alpha[i, t])
        """
        S = len(self.pi)
        L = len(Osequence)
        O = self.find_item(Osequence)
        alpha = np.zeros([S, L])
        ######################################################
        # TODO: compute and return the forward messages alpha
        ######################################################
        for s in range(0, S):
            alpha[s, 0] = self.pi[s] * self.B[s, O[0]]
        for t in range(1, L):
            for s in range(0, S):
                alpha[s, t] = self.B[s, O[t]] * np.sum(self.A[:,s] * alpha[:, t -1])
        return alpha

    def backward(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - beta: (num_state*L) A numpy array where beta[i, t-1] = P(X_{t+1:T}=x_{t+1:T} | Z_t = s_i)
                    (note that this is beta[i, t-1] instead of beta[i, t])
        """
        S = len(self.pi)
        L = len(Osequence)
        O = self.find_item(Osequence)
        beta = np.zeros([S, L])
        #######################################################
        # TODO: compute and return the backward messages beta
        #######################################################
        for s in range(0, S):
            beta[s, L - 1] = 1
        for t in range(L - 2, -1, -1):
            for s in range(0, S):
                beta[s, t] = np.sum(self.A[s] * self.B[:, O[t + 1]] * beta[:, t + 1])
        return beta
    
    def sequence_prob(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - prob: A float number of P(X_{1:T}=x_{1:T})
        """
        
        #####################################################
        # TODO: compute and return prob = P(X_{1:T}=x_{1:T})
        #   using the forward/backward messages
        #####################################################
        alpha = self.forward(Osequence)
        return np.sum(alpha[:, len(Osequence) - 1])

    def posterior_prob(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - gamma: (num_state*L) A numpy array where gamma[i, t-1] = P(Z_t = s_i | X_{1:T}=x_{1:T})
		           (note that this is gamma[i, t-1] instead of gamma[i, t])
        """
        ######################################################################
        # TODO: compute and return gamma using the forward/backward messages
        ######################################################################
        alpha = self.forward(Osequence)
        beta = self.backward(Osequence)
        gamma = (alpha * beta) / np.sum(alpha[:, len(Osequence) - 1])
        return gamma
    
    def likelihood_prob(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - prob: (num_state*num_state*(L-1)) A numpy array where prob[i, j, t-1] = 
                    P(Z_t = s_i, Z_{t+1} = s_j | X_{1:T}=x_{1:T})
        """
        S = len(self.pi)
        L = len(Osequence)
        prob = np.zeros([S, S, L - 1])
        O = self.find_item(Osequence)
        #####################################################################
        # TODO: compute and return prob using the forward/backward messages
        #####################################################################
        alpha = self.forward(Osequence)
        beta = self.backward(Osequence)
        denominator = np.sum(alpha[:, len(Osequence) - 1]);
        for s in range(0, S):
            for s1 in range(0, S):
                for t in range(0, L - 1):
                    prob[s][s1][t] = (alpha[s,t] * self.A[s, s1] * self.B[s1, O[t + 1]] * beta[s1, t + 1]) / denominator
        return prob

    def viterbi(self, Osequence):
        """
        Inputs:
        - Osequence: (1*L) A numpy array of observation sequence with length L

        Returns:
        - path: A List of the most likely hidden states (return actual states instead of their indices;
                    you might find the given function self.find_key useful)
        """
        path = []
        ################################################################################
        # TODO: implement the Viterbi algorithm and return the most likely state path
        ################################################################################
        S = len(self.pi)
        L = len(Osequence)
        delta = np.zeros([S, L])
        D = np.zeros([S, L])
        O = self.find_item(Osequence)
        for s in range(0, S):
            delta[s, 0] = self.pi[s] * self.B[s, O[0]]
        for t in range(1, L):
            for s in range(0, S):
                delta[s, t] = self.B[s, O[t]] * np.max(self.A[:,s] * delta[:, t -1])
                D[s,t] = np.argmax(self.A[:,s] * delta[:, t - 1])
        prev = np.argmax(delta[:, L - 1])
        path.append(self.find_key(self.state_dict, prev))
        for t in range(L - 1, 0, -1):
            path.append(self.find_key(self.state_dict, D[prev, t]))
            prev = int(D[prev, t])
        path.reverse()            
        return path


    #DO NOT MODIFY CODE BELOW
    def find_key(self, obs_dict, idx):
        for item in obs_dict:
            if obs_dict[item] == idx:
                return item

    def find_item(self, Osequence):
        O = []
        for item in Osequence:
            O.append(self.obs_dict[item])
        return O
