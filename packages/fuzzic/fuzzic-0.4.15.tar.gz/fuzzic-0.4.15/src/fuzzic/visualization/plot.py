import matplotlib.pyplot as plt
import numpy as np
import pylab
from matplotlib.ticker import MultipleLocator, PercentFormatter, FixedLocator
import math
from fuzzic.configuration.config import  config


def one_trapeze(sef):
    points = sef.points
    if len(points) == 4:
        return [(points[0].x,points[0].y), (points[1].x,points[1].y), (points[2].x,points[2].y), (points[3].x,points[3].y)]
    else:
        return [(points[0].x,points[0].y), (points[1].x,points[1].y), (points[2].x,points[2].y)]

def one_gaussian(sef):
    d = {"mu" : sef.gaussian.mean,
         "variance" : sef.gaussian.deviation,
         "caption" : sef.label,
         "min" : sef.var.bounds[0],
         "max" : sef.var.bounds[1]}
    return d


def plot_membership_functions(all_sef, captions, variable_name, pas = 10, add_annotation = False, unite=""):
    """
    Plots trapezoidal membership functions given their vertices and adds captions below each function.

    Parameters:
    trapezoids (list of lists of tuples): A list where each element is a list of tuples representing the vertices of a trapezoidal membership function.
                                         Each trapezoid should have 4 vertices.
    captions (list of str): A list of captions to be placed below each membership function.
    """
    fig, ax = plt.subplots(figsize=(config.size_of_plot_x, config.size_of_plot_y), dpi=200)  # Reduced height
    #fig, ax = plt.subplots(figsize=(5, 4), dpi=200)  # Reduced height

    maxi_x_for_unit = all_sef[0].var.bounds[1]

    unite_y = -0.06
    all_sef_ready_to_plot = []
    all_shapes = []
    for sef in all_sef:
        if sef.shape == "gaussian":
            all_sef_ready_to_plot.append(one_gaussian(sef))
            all_shapes.append("gaussian")
        
        else:
            all_sef_ready_to_plot.append(one_trapeze(sef))    
            all_shapes.append("trapezoid")

    colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']  # Colors for the curves
        
    for i, fuzzy_set in enumerate(all_sef_ready_to_plot):
        if all_shapes[i] == "gaussian":
            
            mu = fuzzy_set["mu"]
            variance = fuzzy_set["variance"]
            sigma = math.sqrt(variance)
            x = np.linspace(fuzzy_set["min"], fuzzy_set["max"], 500)
            #plt.plot(x, stats.norm.pdf(x, mu, sigma))
            ax.plot(x, np.exp(-(x - mu)**2 / (2 * sigma**2)), color=colors[i % len(colors)])
            
            # Add caption below the membership function
            caption_x = (x[0] + x[-1]) / 2
            caption_x = mu
            
            
            caption_y = -0.2  # Adjust this value to place the caption below the x-axis
            ax.text(caption_x, caption_y, fuzzy_set["caption"], ha='center', va='center', fontsize=12, fontweight='bold', color=colors[i % len(colors)])
            i = i+1
            
        else:
            
            trapezoid = fuzzy_set
            if len(trapezoid) not in [3,4]:
                raise ValueError("Each trapezoid must have exactly 3 or 4 vertices.")
            
            if len(trapezoid) == 4:
                # Extract the vertices
                (x1, y1), (x2, y2), (x3, y3), (x4, y4) = trapezoid
        
                # Create the x and y values for the trapezoidal membership function
                x = np.linspace(x1, x4, 500)
                y = np.piecewise(x,
                     [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3) & (x < x4), x >= x4],
                     [0, lambda x: (x - x1) / (x2 - x1) * y2, y2, lambda x: (x4 - x) / (x4 - x3) * y2, 0])    
                # Plot the trapezoidal membership function with a unique color
                ax.plot(x, y, color=colors[i % len(colors)])
                
                #add annotation
                if add_annotation:
                    t = 19
                    ax.plot([t,t],[0,0.8], color ='gray',  linewidth=1, linestyle="--")
                    ax.plot([15,19],[0.2,0.2], color ='green',  linewidth=1, linestyle="--")
                    ax.plot([15,19],[0.8,0.8], color ='blue',  linewidth=1, linestyle="--")
                    pylab.annotate(r'$20\%$', xy=(14.7, 0.2),  xycoords='data',
                                   xytext=(+10, +30), textcoords='offset points', fontsize=14, color = "green",
                                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                    pylab.annotate(r'$80\%$', xy=(14.7, 0.8),  xycoords='data',
                                   xytext=(+10, +20), textcoords='offset points', fontsize=14, color = "blue",
                                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                
                
                # Add caption below the membership function
                caption_x = (x2 + x3) / 2
            
            
            else:
                # Extract the vertices
                (x1, y1), (x2, y2), (x3, y3)= trapezoid
        
                # Create the x and y values for the trapezoidal membership function
                x = np.linspace(x1, x3, 500)
                if y1 > 0:
                    #trapeze inferieur
                    y = np.piecewise(x,
                         [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3)],
                         [y1, y1, lambda x: (x3 - x) / (x3 - x2) * y1, 0])    
                    caption_x = (x1 + x2) / 2        
                
                elif y3 > 0:
                    #trapeze supérieur
                    y = np.piecewise(x,
                         [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3)],
                         [0, lambda x: (x - x1) / (x2 - x1) * y3, y3, y3])    
                    caption_x = (x2 + x3) / 2
                else:
                    #triangle
                    y = np.piecewise(x,
                         [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3)],
                         [0, lambda x: (x - x1) / (x2 - x1) * y2, lambda x: (x3 - x) / (x3 - x2) * y2, y3])    
                    caption_x = (x2 + x3) / 2
                    
                    
                # Plot the trapezoidal membership function with a unique color
                ax.plot(x, y, color=colors[i % len(colors)])
                
            ax.set_ylim(0, 1.1)
            
            caption_y = -0.2  # Adjust this value to place the caption below the x-axis
            ax.text(caption_x, caption_y, captions[i], ha='center', va='center', fontsize=12, fontweight='bold', color=colors[i % len(colors)])
            i = i+1
    
    ax.text(maxi_x_for_unit + pas, unite_y + 0.06, unite, ha='center', va='center', fontsize=12, color="black")

    # Add grid with precise intervals
    
    pas_x_axis = pas
    
#    ax.xaxis.set_major_locator(MultipleLocator(pas_x_axis))  # Major grid every 1 unit
#    ax.xaxis.set_minor_locator(MultipleLocator(pas_x_axis))  # Minor grid every 0.5 units
    ax.yaxis.set_major_locator(FixedLocator([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))  # Major grid at specific intervals
    ax.grid(which='major', linestyle='--', linewidth=0.5)

    # Set y-axis to show percentages
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    # Set aspect ratio to be equal
    ax.set_aspect('auto', adjustable='box')

    # Label the y-axis
    ax.set_ylabel("Membership degree (%)")
    ax.set_title(variable_name + " - rulebase : " + all_sef[0].var.rulebase.label)

    # Save the plot in high resolution
    #plt.savefig('trapezoidal_membership_functions.png', dpi=300)

    plt.show()



























# Archive
# def plot_trapezoidal_membership_functions(trapezoids, captions, variable_name, pas = 10, add_annotation = False, gaussian = None, unite=""):
#     """
#     Plots trapezoidal membership functions given their vertices and adds captions below each function.
#
#     Parameters:
#     trapezoids (list of lists of tuples): A list where each element is a list of tuples representing the vertices of a trapezoidal membership function.
#                                          Each trapezoid should have 4 vertices.
#     captions (list of str): A list of captions to be placed below each membership function.
#     """
#     fig, ax = plt.subplots(figsize=(10, 4), dpi=200)  # Reduced height
#     #fig, ax = plt.subplots(figsize=(5, 4), dpi=200)  # Reduced height
#
#     unite_y = -0.06
#
#     trapezoids = [one_trapeze(t) for t in trapezoids]
#
#     colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']  # Colors for the curves
#
#     for i, trapezoid in enumerate(trapezoids):
#         if len(trapezoid) not in [3,4]:
#             raise ValueError("Each trapezoid must have exactly 3 or 4 vertices.")
#
#         if len(trapezoid) == 4:
#             # Extract the vertices
#             (x1, y1), (x2, y2), (x3, y3), (x4, y4) = trapezoid
#             maxi_x = x4
#
#             # Create the x and y values for the trapezoidal membership function
#             x = np.linspace(x1, x4, 500)
#             y = np.piecewise(x,
#                  [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3) & (x < x4), x >= x4],
#                  [0, lambda x: (x - x1) / (x2 - x1) * y2, y2, lambda x: (x4 - x) / (x4 - x3) * y2, 0])
#             # Plot the trapezoidal membership function with a unique color
#             ax.plot(x, y, color=colors[i % len(colors)])
#
#             #add annotation
#             if add_annotation:
#                 t = 19
#                 ax.plot([t,t],[0,0.8], color ='gray',  linewidth=1, linestyle="--")
#                 ax.plot([15,19],[0.2,0.2], color ='green',  linewidth=1, linestyle="--")
#                 ax.plot([15,19],[0.8,0.8], color ='blue',  linewidth=1, linestyle="--")
#                 pylab.annotate(r'$20\%$', xy=(14.7, 0.2),  xycoords='data',
#                                xytext=(+10, +30), textcoords='offset points', fontsize=14, color = "green",
#                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
#                 pylab.annotate(r'$80\%$', xy=(14.7, 0.8),  xycoords='data',
#                                xytext=(+10, +20), textcoords='offset points', fontsize=14, color = "blue",
#                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
#
#
#             # Add caption below the membership function
#             caption_x = (x2 + x3) / 2
#
#
#         else:
#             # Extract the vertices
#             (x1, y1), (x2, y2), (x3, y3)= trapezoid
#             maxi_x = x3
#
#             # Create the x and y values for the trapezoidal membership function
#             x = np.linspace(x1, x3, 500)
#             if y1 > 0:
#                 y = np.piecewise(x,
#                      [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3)],
#                      [y1, y1, lambda x: (x3 - x) / (x3 - x2) * y1, 0])
#                 caption_x = (x1 + x2) / 2
#
#             else:
#                 y = np.piecewise(x,
#                      [x < x1, (x >= x1) & (x < x2), (x >= x2) & (x < x3), (x >= x3)],
#                      [0, lambda x: (x - x1) / (x2 - x1) * y3, y3, y3])
#                 caption_x = (x2 + x3) / 2
#
#
#             # Plot the trapezoidal membership function with a unique color
#             ax.plot(x, y, color=colors[i % len(colors)])
#         ax.set_ylim(0, 1.1)
#
#         caption_y = -0.2  # Adjust this value to place the caption below the x-axis
#         ax.text(caption_x, caption_y, captions[i], ha='center', va='center', fontsize=12, fontweight='bold', color=colors[i % len(colors)])
#     ax.text(maxi_x + pas, unite_y, unite, ha='center', va='center', fontsize=12, color="black")
#
#     # Add grid with precise intervals
#
#     pas_x_axis = pas
#
#     ax.xaxis.set_major_locator(MultipleLocator(pas_x_axis))  # Major grid every 1 unit
#     ax.xaxis.set_minor_locator(MultipleLocator(pas_x_axis))  # Minor grid every 0.5 units
#     ax.yaxis.set_major_locator(FixedLocator([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))  # Major grid at specific intervals
#     ax.grid(which='major', linestyle='--', linewidth=0.5)
#
#     # Set y-axis to show percentages
#     ax.yaxis.set_major_formatter(PercentFormatter(1))
#
#     # Set aspect ratio to be equal
#     ax.set_aspect('auto', adjustable='box')
#
#     # Label the y-axis
#     ax.set_ylabel("Membership degree (%)")
#     ax.set_title(variable_name)
#
#     # Save the plot in high resolution
#     #plt.savefig('trapezoidal_membership_functions.png', dpi=300)
#
#     plt.show()
#
#
# def plot_gaussian_membership_functions(gaussians, variable_name, pas = 10, unite=""):
#     """
#     Plots trapezoidal membership functions given their vertices and adds captions below each function.
#
#     Parameters:
#     trapezoids (list of lists of tuples): A list where each element is a list of tuples representing the vertices of a trapezoidal membership function.
#                                          Each trapezoid should have 4 vertices.
#     captions (list of str): A list of captions to be placed below each membership function.
#     """
#     fig, ax = plt.subplots(figsize=(5, 4), dpi=200)  # Reduced height
#     unite_y = 0
#
#     gaussians = [one_gaussian(t) for t in gaussians]
#
#     colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']  # Colors for the curves
#
#     i = 0
#     for gaussian in gaussians:
#
#         mu = gaussian["mu"]
#         variance = gaussian["variance"]
#         sigma = math.sqrt(variance)
#         x = np.linspace(gaussian["min"], gaussian["max"], 100)
#         #plt.plot(x, stats.norm.pdf(x, mu, sigma))
#         plt.plot(x, np.exp(-(x - mu)**2 / (2 * sigma**2)))
#
#         # Add caption below the membership function
#         caption_x = (x[0] + x[-1]) / 2
#
#
#         caption_y = -0.2  # Adjust this value to place the caption below the x-axis
#         ax.text(caption_x, caption_y, gaussian["caption"], ha='center', va='center', fontsize=12, fontweight='bold', color=colors[i % len(colors)])
#         i = i+1
#
#     ax.text(gaussian["max"] + pas, unite_y, unite, ha='center', va='center', fontsize=12, color="black")
#
#     # Add grid with precise intervals
#     ax.set_ylim(0, 1.1)
#     pas_x_axis = pas
#
#     ax.xaxis.set_major_locator(MultipleLocator(pas_x_axis))  # Major grid every 1 unit
#     ax.xaxis.set_minor_locator(MultipleLocator(pas_x_axis))  # Minor grid every 0.5 units
#     ax.yaxis.set_major_locator(FixedLocator([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))  # Major grid at specific intervals
#     ax.grid(which='major', linestyle='--', linewidth=0.5)
#
#     # Set y-axis to show percentages
#     ax.yaxis.set_major_formatter(PercentFormatter(1))
#
#     # Set aspect ratio to be equal
#     ax.set_aspect('auto', adjustable='box')
#
#     # Label the y-axis
#     ax.set_ylabel("Degré d'appartenance (%)")
#     ax.set_title(variable_name)
#
#     # Save the plot in high resolution
#     #plt.savefig('trapezoidal_membership_functions.png', dpi=300)
#
#     plt.show()
#
#
#
# def one_trapeze(a,b,c,d=-1, hauteur = 1, style = "normal"):
#     if style == "normal":
#         return [(a,0), (b,hauteur), (c, hauteur), (d,0)]
#     elif style == "inf":
#         return [(a,hauteur), (b,hauteur), (c, 0)]
#     else:
#         return [(a,0), (b,hauteur), (c, hauteur)]
#
# def one_gaussian(mu, variance, caption, minimum, maximum):
#     d = {"mu" : mu,
#          "variance" : variance,
#          "caption" : caption,
#          "min" : minimum,
#          "max" : maximum}
#     return d
#
#
#
#
#
#
# def exemple():
#     autoroute_3 = [
#         one_trapeze(30,65,75, hauteur = 0.6, style = "inf"),
#         one_trapeze(65,75,115,125,hauteur = 0.6,),
#         one_trapeze(125,130,180,hauteur = 0.6, style = "sup")
#     ]
#
#     captions = ["basse", "modérée", "élevé"]
#     variable_name = "vitesse"
#     plot_trapezoidal_membership_functions(autoroute_3, captions, variable_name)






