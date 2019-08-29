
from KerasSingleLaneExperiment.mlp_deepFogGuard_health import define_deepFogGuard_MLP
from KerasSingleLaneExperiment.FailureIteration import calculateExpectedAccuracy
from KerasSingleLaneExperiment.main import average
from KerasSingleLaneExperiment.health_common_exp_methods import init_data, init_common_experiment_params, convert_to_string
import keras.backend as K
import gc
import os
from keras.callbacks import ModelCheckpoint

# runs all 3 failure configurations for all 3 models
if __name__ == "__main__":
    use_GCP = True
    training_data, test_data, training_labels, test_labels, val_data, val_labels = init_data(use_GCP)

    num_iterations, num_vars, num_classes, survivability_settings, num_train_epochs, hidden_units, batch_size = init_common_experiment_params(training_data)
    
    # define weight schemes
    one_weight_scheme = 1
    normalized_survivability_weight_scheme = 2
    survivability_weight_scheme = 3
    random_weight_scheme = 4
    random_weight_scheme2 = 5
    fifty_weight_scheme = 6
    weight_schemes = [
        one_weight_scheme,
        normalized_survivability_weight_scheme,
        survivability_weight_scheme,
        random_weight_scheme,
        random_weight_scheme2,
        fifty_weight_scheme,
    ]
   
    load_model = False
    # file name with the experiments accuracy output
    output_name = "results/health_hyperconnection_fixed_random_weight.txt"
    verbose = 2
    hyperconnection_weightedbysurvivability_config = 2
    # keep track of output so that output is in order
    output_list = []
    
    no_failure, normal, poor, hazardous = convert_to_string(survivability_settings)

    # dictionary to store all the results
    output = {
        "DeepFogGuard Hyperconnection Weight": 
        {
            one_weight_scheme:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            },
            normalized_survivability_weight_scheme:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            },
            survivability_weight_scheme:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            },
            random_weight_scheme:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            },
            random_weight_scheme2:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            },
            fifty_weight_scheme:
            {
                no_failure: [0] * num_iterations,
                hazardous:[0] * num_iterations,
                poor:[0] * num_iterations,
                normal:[0] * num_iterations,
            }
        },
    }

    # make folder for outputs 
    if not os.path.exists('results/'):
        os.mkdir('results/')
    for iteration in range(1,num_iterations+1):   
        output_list.append('ITERATION ' + str(iteration) +  '\n')
        print("ITERATION ", iteration)
        for survivability_setting in survivability_settings:
            # loop through all the weight schemes
            for weight_scheme in weight_schemes:
                # deepFogGuard hyperconnection weight 
                deepFogGuard_hyperconnection_weight = define_deepFogGuard_MLP(num_vars,num_classes,hidden_units,survivability_setting, hyperconnection_weights_scheme = weight_scheme)
                deepFogGuard_hyperconnection_weight_file = str(iteration) + "_" + str(survivability_setting) + "_" + str(weight_scheme) + 'health_hyperconnection_fixed_random_weight.h5'
                if load_model:
                    deepFogGuard_hyperconnection_weight.load_weights(deepFogGuard_hyperconnection_weight_file)
                else:
                    print("DeepFogGuard Hyperconnection Weight")
                    deepFogGuard_hyperconnection_weight_CheckPoint = ModelCheckpoint(deepFogGuard_hyperconnection_weight_file, monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=True, mode='auto', period=1)
                    deepFogGuard_hyperconnection_weight.fit(training_data,training_labels,epochs=num_train_epochs, batch_size=batch_size,verbose=verbose,shuffle = True, callbacks = [deepFogGuard_hyperconnection_weight_CheckPoint],validation_data=(val_data,val_labels))
                    # load weights from epoch with the highest val acc
                    deepFogGuard_hyperconnection_weight.load_weights(deepFogGuard_hyperconnection_weight_file)
                output["DeepFogGuard Hyperconnection Weight"][weight_scheme][str(survivability_setting)][iteration-1] = calculateExpectedAccuracy(deepFogGuard_hyperconnection_weight,survivability_setting,output_list,training_labels,test_data,test_labels)
                # clear session so that model will recycled back into memory
                K.clear_session()
                gc.collect()
                del deepFogGuard_hyperconnection_weight
   # calculate average accuracies 
    for survivability_setting in survivability_settings:
        for weight_scheme in weight_schemes:
            deepFogGuard_hyperconnection_weight_acc = average(output["DeepFogGuard Hyperconnection Weight"][weight_scheme][str(survivability_setting)])
            output_list.append(str(survivability_setting) + str(weight_scheme) + " DeepFogGuard Hyperconnection Weight: " + str(deepFogGuard_hyperconnection_weight_acc) + '\n')
            print(str(survivability_setting),weight_scheme,"DeepFogGuard Hyperconnection Weight:",deepFogGuard_hyperconnection_weight_acc)
    # write experiments output to file
    with open(output_name,'w') as file:
        file.writelines(output_list)
        file.flush()
        os.fsync(file)
    if use_GCP:
        os.system('gsutil -m -q cp -r {} gs://anrl-storage/results/'.format(output_name))
        os.system('gsutil -m -q cp -r *.h5 gs://anrl-storage/models')
