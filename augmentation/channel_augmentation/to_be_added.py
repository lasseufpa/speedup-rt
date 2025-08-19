    elif args.plot_type == 'bitrate':
        orig_channel_eigenvalues = [get_svd_matrix(channel) for channel
                                            in orig_wireless_channels[:-2]]
        predicted_channel_eigenvalues = [get_svd_matrix(channel) for channel
                                            in predicted_wireless_channels[:-2]]

        orig_bitrate = [get_bitrate(np.array(orig_channel_eigenvalues[i])) / 1e6
                        for i in range(len(orig_channel_eigenvalues))]

        predicted_bitrate = [get_bitrate(np.array(predicted_channel_eigenvalues[i])) / 1e6
                        for i in range(len(predicted_channel_eigenvalues))]

        '''
        eq_orig_channel_magnitude = [np.abs(equivalent_channel(channel, 
                                                            N_TX_ANTENNAS, N_RX_ANTENNAS))
                                            for channel in orig_wireless_channels[:-2]]
        orig_best_beam = [np.squeeze(get_best_beam(channel_magnitude)) for channel_magnitude
                                                        in eq_orig_channel_magnitude]
        orig_bitrate = [get_bitrate(channel_magnitude) / 1e6 for channel_magnitude
                                                        in eq_orig_channel_magnitude]
        # get best original bitrate
        best_orig_bitrate = [orig_bitrate[i][orig_best_beam[i][0]][orig_best_beam[i][1]]
                            for i in range(len(orig_bitrate))]

        eq_predicted_channel_magnitude = [np.abs(equivalent_channel(channel,
                                                            N_TX_ANTENNAS, N_RX_ANTENNAS))
                                            for channel in predicted_wireless_channels[:-2]]
        predicted_best_beam = [np.squeeze(get_best_beam(channel_magnitude)) for channel_magnitude
                                                        in eq_predicted_channel_magnitude]
        predicted_bitrate = [get_bitrate(channel_magnitude) / 1e6 for channel_magnitude
                                                        in eq_predicted_channel_magnitude]

        # get best predicted bitrate
        best_predicted_bitrate = [predicted_bitrate[i][predicted_best_beam[i][0]][predicted_best_beam[i][1]]
                            for i in range(len(predicted_bitrate))]

        '''
        plt.plot(predicted_bitrate[1::2], label='Estimated channel bitrate', marker='s')
        plt.plot(orig_bitrate[1::2], label='Original channel bitrate', marker='x')
        #plt.scatter(np.arange(1, len(orig_bitrate), 2),
        #            predicted_bitrate[1::2], s=24, label='Especific estimated bitrate')
        plt.legend()
        plt.grid()
        plt.title(f'{args.scenario.title()} scenario')
        plt.xlabel('Scene', fontsize=15)
        plt.ylabel('Bitrate (Mbits/s)', fontsize=15)
        plt.savefig(f'results/bitrate_{args.interp_type}_{args.scenario}.png', dpi=200, bbox_inches='tight')