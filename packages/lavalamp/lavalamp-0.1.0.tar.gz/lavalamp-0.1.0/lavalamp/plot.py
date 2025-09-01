import numpy as np
import matplotlib.pyplot as plt
import lavalamp as ll


histogram_bins = 1000
histogram_plot_bins = 100

plot_colors = ["#0063a5", '#ffae49', '#44b7c2', '#c44e52', '#b5d63d', '#14848f']

def stacked(*args):
    f = plt.figure()
    bins = histogram_plot_bins
    
    for i, x in enumerate(args):
        plot(x,
             color_index=i,
             plot_sugar=False)
    
    # plot sugar
    title = ' vs '.join([x.label for x in args])
    plt.title(title)
    plt.yticks([])

    # determine legend from labels if they exist
    legend = []
    for x in args:
        legend.append('')
        legend.append(x.label)
    plt.legend(legend)
        
def plot(ll_obj, color_index=0, plot_sugar=True):


    c = plot_colors[color_index]
    # title = f'{ll_obj.label}' if ll_obj.label else ''

    # discrete random variables have a different way of plotting
    if isinstance(ll_obj, ll.DiscreteUniform):
        n, bins, patches = plt.hist(ll_obj.values,
                                    bins=100,
                                    density=True,
                                    color=c,
                                    alpha=0.7)
        # plot sugar
        plt.title(ll_obj.label)
        plt.xticks(np.unique(ll_obj.values))
        plt.yticks([np.max(n)], labels=[f'{np.max(n)/np.sum(n):.2f}'])
        return

    hist, edges = np.histogram(ll_obj.values,
                               bins=histogram_plot_bins,
                               density=True)
    dx = edges[1] - edges[0]
    x = edges[:-1] + dx / 2
    x = np.insert(x, 0, x[0])
    x = np.append(x, x[-1])
    hist = np.insert(hist, 0, 0)
    hist = np.append(hist, 0)

    plt.plot(x, hist, color=c, label=str())
    plt.fill(x, hist, color=c, alpha=0.5)

    # plot sugar
    if plot_sugar:
        plt.title(ll_obj.label)
        plt.xticks([ll_obj.min, ll_obj.mean, ll_obj.max])
        plt.gca().set_ylim(ymin=0)
        plt.yticks([])

def multiple(*args):
    
    variable_count = len(args)
    column_count = int(np.ceil(np.sqrt(variable_count)))
    row_count = int(np.ceil(variable_count / column_count))

    f = plt.figure()

    for i, x in enumerate(args):
        plt.subplot(row_count, column_count, i+1)
        plot(x)
        # plt.hist(x.values, bins=ll.histogram_plot_bins, density=True)
    plt.tight_layout()
    

def show():
    plt.show()

