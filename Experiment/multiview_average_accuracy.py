
from Experiment.mlp_deepFogGuardPlus_camera import define_deepFogGuardPlus_MLP
from Experiment.mlp_deepFogGuard_camera import define_deepFogGuard_MLP
from Experiment.mlp_Vanilla_camera import define_vanilla_model_MLP
from Experiment.FailureIterationFromImageDataGenerator import calculateExpectedAccuracyFromImageGenerator
from Experiment.utility import average, get_model_weights_MLP_camera
from Experiment.multiview_common_exp_methods import init_data, init_common_experiment_params
from Experiment.common_exp_methods import write_n_upload
from Experiment.utility import get_model_weights_MLP_health
from Experiment.common_exp_methods import convert_to_string, make_output_dictionary_average_accuracy
import keras.backend as K
import datetime
import gc
import os

def define_and_train(iteration, model_name, load_model,train_generator, val_generator, input_shape, num_classes, hidden_units, verbose, default_failout_survival_rate, default_survivability_setting, allpresent_skip_hyperconnections_configuration):
    # ResiliNet
    if model_name == "ResiliNet":
        model = define_deepFogGuardPlus_MLP(input_shape,num_classes,hidden_units,default_failout_survival_rate)
        model_file = "new_split_" + str(iteration) + '_deepFogGuardPlus.h5'
    # deepFogGuard
    if model_name == "deepFogGuard":
        model = define_deepFogGuard_MLP(input_shape, num_classes, hidden_units, default_survivability_setting, allpresent_skip_hyperconnections_configuration)
        model_file = "new_split_" + str(iteration) + '_deepFogGuard.h5'
    # Vanilla model
    if model_name == "Vanilla":
        model = define_vanilla_model_MLP(input_shape,num_classes,hidden_units)
        model_file = "new_split_" + str(iteration) + '_vanilla.h5'
    
    get_model_weights_MLP_camera(model, model_name, load_model, model_file, train_generator, val_generator, verbose)
    return model

def calc_accuracy(iteration, model_name, model, survivability_setting, output_list,test_generator, num_test_examples):
    output_list.append(model_name + "\n")
    print(model_name)
    output[model_name][str(survivability_setting)][iteration-1] = calculateExpectedAccuracyFromImageGenerator(model,survivability_setting,output_list,test_generator,num_test_examples = num_test_examples)


# runs all 3 failure configurations for all 3 models
if __name__ == "__main__":
    use_GCP = True
    train_generator, val_generator, test_generator = init_data(use_GCP) 
    num_train_examples,num_val_examples,num_test_examples, survivability_settings, input_shape, num_classes, hidden_units = init_common_experiment_params()

    default_failout_survival_rate = [.95,.95,.95]
    allpresent_skip_hyperconnections_configuration = [1,1,1]
    default_survivability_setting = [1,1,1]
    load_model = False

    # file name with the experiments accuracy output
    output_name = "results/health_normal_testfordfg.txt"
    num_iterations = 1
    verbose = 2

    # keep track of output so that output is in order
    output_list = []
    
    output = make_output_dictionary_average_accuracy(survivability_settings, num_iterations)

    # make folder for outputs 
    if not os.path.exists('results/'):
        os.mkdir('results/')
    for iteration in range(1,num_iterations+1):   
        output_list.append('ITERATION ' + str(iteration) +  '\n')
        print("ITERATION ", iteration)
        ResiliNet = define_and_train(iteration, "ResiliNet", load_model, train_generator, val_generator, input_shape, num_classes, hidden_units, verbose, default_failout_survival_rate, default_survivability_setting, allpresent_skip_hyperconnections_configuration)
        deepFogGuard = define_and_train(iteration, "deepFogGuard", load_model, train_generator, val_generator, input_shape, num_classes, hidden_units, verbose, default_failout_survival_rate, default_survivability_setting, allpresent_skip_hyperconnections_configuration)
        Vanilla = define_and_train(iteration, "Vanilla", load_model, train_generator,val_generator, input_shape, num_classes, hidden_units, verbose, default_failout_survival_rate, default_survivability_setting, allpresent_skip_hyperconnections_configuration)
 
        # test models
        for survivability_setting in survivability_settings:
            calc_accuracy(iteration, "ResiliNet", ResiliNet, survivability_setting, output_list,test_generator, num_test_examples)
            calc_accuracy(iteration, "deepFogGuard", deepFogGuard, survivability_setting, output_list,test_generator, num_test_examples)
            calc_accuracy(iteration, "Vanilla", Vanilla, survivability_setting, output_list,test_generator, num_test_examples)
            
        # clear session so that model will recycled back into memory
        K.clear_session()
        gc.collect()
        del deepFogGuard
        del ResiliNet
        del Vanilla
   # calculate average accuracies from all expected accuracies
    for survivability_setting in survivability_settings:
        ResiliNet_acc = average(output["ResiliNet"][str(survivability_setting)])
        deepFogGuard_acc = average(output["deepFogGuard"][str(survivability_setting)])
        Vanilla_acc = average(output["Vanilla"][str(survivability_setting)])

        output_list.append(str(survivability_setting) + " ResiliNet Accuracy: " + str(ResiliNet_acc) + '\n')
        output_list.append(str(survivability_setting) + " deepFogGuard Accuracy: " + str(deepFogGuard_acc) + '\n')
        output_list.append(str(survivability_setting) + " Vanilla Accuracy: " + str(Vanilla_acc) + '\n')

        print(str(survivability_setting),"ResiliNet Accuracy:",ResiliNet_acc)
        print(str(survivability_setting),"deepFogGuard Accuracy:",deepFogGuard_acc)
        print(str(survivability_setting),"Vanilla Accuracy:",Vanilla_acc)

    write_n_upload(output_name, output_list, use_GCP)
    print(output)