# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# class CNN:
#     """
#     A class for building and training a Convolutional Neural Network (CNN) for classification tasks using flex-sweep input statistics.

#     Attributes:
#         train_data (str or pl.DataFrame): Path to the training data file or a pandas DataFrame containing the training data.
#         test_data (pl.DataFrame): DataFrame containing test data after being loaded from a file.
#         output_folder (str): Directory where the trained model and history will be saved.
#         num_stats (int): Number of statistics/features in the training data. Default is 11.
#         center (np.ndarray): Array defining the center positions for processing. Default ranges from 500000 to 700000.
#         windows (np.ndarray): Array defining the window sizes for the CNN. Default values are [50000, 100000, 200000, 500000, 1000000].
#         train_split (float): Fraction of the training data used for training. Default is 0.8.
#         model (tf.keras.Model): Keras model instance for the CNN.
#         gpu (bool): Indicates whether to use GPU for training. Default is True.
#     """

#     def __init__(self, train_data=None, test_data=None, output_folder=None, model=None):
#         """
#         Initializes the CNN class with training data and output folder.

#         Args:
#             train_data (str or pl.DataFrame): Path to the training data file or a pandas DataFrame containing the training data.
#             output_folder (str): Directory to save the trained model and history.
#         """
#         # self.sweep_data = sweep_data
#         self.train_data = train_data
#         self.test_data = test_data
#         self.output_folder = output_folder
#         self.output_prediction = "predictions.txt"
#         self.num_stats = 11
#         self.center = np.arange(5e5, 7e5 + 1e4, 1e4).astype(int)
#         self.windows = np.array([50000, 100000, 200000, 500000, 1000000])
#         self.train_split = 0.8
#         self.prediction = None
#         self.history = None
#         self.model = model
#         self.gpu = True
#         self.tf = None

#     def check_tf(self):
#         """
#         Checks and imports the TensorFlow library.

#         Returns:
#             tf.Module: The TensorFlow module.
#         """
#         if self.gpu is False:
#             os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
#         tf = importlib.import_module("tensorflow")
#         return tf

#     def cnn_flexsweep(self, model_input, num_classes=2):
#         """
#         Flex-sweep CNN architecture with multiple convolutional and pooling layers.

#         Args:
#             input_shape (tuple): Shape of the input data, e.g., (224, 224, 3). Default Flex-sweep input statistics, windows and centers
#             num_classes (int): Number of output classes in the classification problem. Default: Flex-sweep binary classification

#         Returns:
#             Model: A Keras model instance representing the Flex-sweep CNN architecture.
#         """
#
#         # 3x3 layer
#         layer1 = tf.keras.layers.Conv2D(
#             64,
#             3,
#             padding="same",
#             name="convlayer1_1",
#             kernel_initializer="glorot_uniform",
#         )(model_input)
#         layer1 = tf.keras.layers.ReLU(negative_slope=0)(layer1)
#         layer1 = tf.keras.layers.Conv2D(
#             128,
#             3,
#             padding="same",
#             name="convlayer1_2",
#             kernel_initializer="glorot_uniform",
#         )(layer1)
#         layer1 = tf.keras.layers.ReLU(negative_slope=0)(layer1)
#         layer1 = tf.keras.layers.Conv2D(256, 3, padding="same", name="convlayer1_3")(
#             layer1
#         )
#         layer1 = tf.keras.layers.ReLU(negative_slope=0)(layer1)
#         layer1 = tf.keras.layers.MaxPooling2D(
#             pool_size=3, name="poollayer1", padding="same"
#         )(layer1)
#         layer1 = tf.keras.layers.Dropout(0.15, name="droplayer1")(layer1)
#         layer1 = tf.keras.layers.Flatten(name="flatlayer1")(layer1)

#         # 2x2 layer with 1x3 dilation
#         layer2 = tf.keras.layers.Conv2D(
#             64,
#             2,
#             dilation_rate=[1, 3],
#             padding="same",
#             name="convlayer2_1",
#             kernel_initializer="glorot_uniform",
#         )(model_input)
#         layer2 = tf.keras.layers.ReLU(negative_slope=0)(layer2)
#         layer2 = tf.keras.layers.Conv2D(
#             128,
#             2,
#             dilation_rate=[1, 3],
#             padding="same",
#             name="convlayer2_2",
#             kernel_initializer="glorot_uniform",
#         )(layer2)
#         layer2 = tf.keras.layers.ReLU(negative_slope=0)(layer2)
#         layer2 = tf.keras.layers.Conv2D(
#             256, 2, dilation_rate=[1, 3], padding="same", name="convlayer2_3"
#         )(layer2)
#         layer2 = tf.keras.layers.ReLU(negative_slope=0)(layer2)
#         layer2 = tf.keras.layers.MaxPooling2D(pool_size=2, name="poollayer2")(layer2)
#         layer2 = tf.keras.layers.Dropout(0.15, name="droplayer2")(layer2)
#         layer2 = tf.keras.layers.Flatten(name="flatlayer2")(layer2)

#         # 2x2 with 1x5 dilation
#         layer3 = tf.keras.layers.Conv2D(
#             64,
#             2,
#             dilation_rate=[1, 5],
#             padding="same",
#             name="convlayer4_1",
#             kernel_initializer="glorot_uniform",
#         )(model_input)
#         layer3 = tf.keras.layers.ReLU(negative_slope=0)(layer3)
#         layer3 = tf.keras.layers.Conv2D(
#             128,
#             2,
#             dilation_rate=[1, 5],
#             padding="same",
#             name="convlayer4_2",
#             kernel_initializer="glorot_uniform",
#         )(layer3)
#         layer3 = tf.keras.layers.ReLU(negative_slope=0)(layer3)
#         layer3 = tf.keras.layers.Conv2D(
#             256, 2, dilation_rate=[1, 5], padding="same", name="convlayer4_3"
#         )(layer3)
#         layer3 = tf.keras.layers.ReLU(negative_slope=0)(layer3)
#         layer3 = tf.keras.layers.MaxPooling2D(pool_size=2, name="poollayer3")(layer3)
#         layer3 = tf.keras.layers.Dropout(0.15, name="droplayer3")(layer3)
#         layer3 = tf.keras.layers.Flatten(name="flatlayer3")(layer3)

#         # concatenate convolution layers
#         concat = tf.keras.layers.concatenate([layer1, layer2, layer3])
#         concat = tf.keras.layers.Dense(512, name="512dense", activation="relu")(concat)
#         concat = tf.keras.layers.Dropout(0.2, name="dropconcat1")(concat)
#         concat = tf.keras.layers.Dense(128, name="last_dense", activation="relu")(
#             concat
#         )
#         concat = tf.keras.layers.Dropout(0.2 / 2, name="dropconcat2")(concat)
#         output = tf.keras.layers.Dense(
#             num_classes,
#             name="out_dense",
#             activation="sigmoid",
#             kernel_initializer="glorot_uniform",
#         )(concat)

#         return output

#     def load_training_data(self):
#         """
#         Loads training data from specified files and preprocesses it for training.

#         Returns:
#             tuple: Contains the training and validation datasets:
#                 - X_train (np.ndarray): Input features for training.
#                 - X_test (np.ndarray): Input features for testing.
#                 - Y_train (np.ndarray): One-hot encoded labels for training.
#                 - Y_test (np.ndarray): One-hot encoded labels for testing.
#                 - X_valid (np.ndarray): Input features for validation.
#                 - Y_valid (np.ndarray): One-hot encoded labels for validation.
#         """
#

#         assert self.train_data is not None, "Please input training data"
#         assert (
#             "txt" in self.train_data
#             or "csv" in self.train_data
#             or self.train_data.endswith(".parquet")
#         ), "Please save your dataframe as CSV or parquet"

#         if isinstance(self.train_data, pl.DataFrame):
#             pass
#         elif self.train_data.endswith(".gz"):
#             tmp = pl.read_csv(self.train_data, separator=",")
#         elif self.train_data.endswith(".parquet"):
#             tmp = pl.read_parquet(self.train_data)

#         if self.num_stats < 17:
#             tmp = tmp.select([col for col in tmp.columns if "flip" not in col])

#         tmp = tmp.with_columns(
#             pl.when((pl.col("model") != "neutral"))
#             .then(pl.lit("sweep"))
#             .otherwise(pl.lit("neutral"))
#             .alias("model")
#         )
#         tmp = tmp.filter(
#             ((pl.col("f_t") >= 0.4) & (pl.col("model") == "sweep"))
#             | (pl.col("model") == "neutral")
#         )

#         sweep_parameters = tmp.filter("model" != "neutral").select(tmp.columns[:5])

#         stats = ["iter", "model"]
#         _stats = [
#             "dind",
#             "haf",
#             "hapdaf_o",
#             "isafe",
#             "high_freq",
#             "hapdaf_s",
#             "nsl",
#             "s_ratio",
#             "low_freq",
#             "ihs",
#             "h12",
#         ]

#         stats = stats + _stats
#         train_stats = []
#         for i in stats:
#             # train_stats.append(df_train.iloc[:, df_train.columns.str.contains(i)])
#             if i == "ihs":
#                 train_stats.append(
#                     tmp.select(pl.col("^.*" + i + ".*$")).select(
#                         pl.exclude("^.*hapbin.*$")
#                     )
#                 )
#             # elif i == 'haf' or i == 'h12':
#             #     train_stats.append(df_train.select(pl.col("^.*" + i + ".*600000$")))
#             else:
#                 train_stats.append(tmp.select(pl.col("^.*" + i + ".*$")))
#         train_stats = pl.concat(train_stats, how="horizontal").select(
#             pl.exclude("^.*ihh.*$")
#         )
#         train_stats = pl.concat(
#             [tmp.select("s", "f_i", "f_t", "t"), train_stats], how="horizontal"
#         )

#         y = train_stats.select(
#             (pl.col("model").str.contains("neutral").cast(pl.Int8)).alias(
#                 "neutral_flag"
#             )
#         )["neutral_flag"].to_numpy()

#         test_split = round(1 - self.train_split, 2)

#         X_train, X_test, y_train, y_test = train_test_split(
#             train_stats, y, test_size=test_split, shuffle=True
#         )

#         X_train = (
#             X_train.select(train_stats.columns[6:])
#             .to_numpy()
#             .reshape(
#                 X_train.shape[0],
#                 self.num_stats,
#                 self.windows.size * self.center.size,
#                 1,
#             )
#         )
#         Y_train = tf.keras.utils.to_categorical(y_train, 2)
#         Y_test = tf.keras.utils.to_categorical(y_test, 2)

#         X_valid, X_test, Y_valid, Y_test = train_test_split(
#             X_test, Y_test, test_size=0.5
#         )

#         X_test_params = X_test.select(X_test.columns[:6])
#         X_test = (
#             X_test.select(train_stats.columns[6:])
#             .to_numpy()
#             .reshape(
#                 X_test.shape[0],
#                 self.num_stats,
#                 self.windows.size * self.center.size,
#                 1,
#             )
#         )
#         X_valid = (
#             X_valid.select(train_stats.columns[6:])
#             .to_numpy()
#             .reshape(
#                 X_valid.shape[0],
#                 self.num_stats,
#                 self.windows.size * self.center.size,
#                 1,
#             )
#         )

#         self.test_data = [X_test, X_test_params, Y_test]

#         return X_train, X_test, Y_train, Y_test, X_valid, Y_valid

#     def train(self, cnn=None):
#         """
#         Trains the CNN model on the training data.

#         This method preprocesses the data, sets up data augmentation, defines the model architecture,
#         compiles the model, and fits it to the training data while saving the best model and training history.
#         """
#

#         if cnn is None:
#             cnn = self.cnn_flexsweep

#         (X_train, X_test, Y_train, Y_test, X_valid, Y_valid) = self.load_training_data()

#         datagen = tf.keras.preprocessing.image.ImageDataGenerator(
#             featurewise_center=True,
#             featurewise_std_normalization=True,
#             horizontal_flip=True,
#         )

#         validation_gen = tf.keras.preprocessing.image.ImageDataGenerator(
#             featurewise_center=True,
#             featurewise_std_normalization=True,
#             horizontal_flip=False,
#         )

#         test_gen = tf.keras.preprocessing.image.ImageDataGenerator(
#             featurewise_center=True,
#             featurewise_std_normalization=True,
#             horizontal_flip=False,
#         )

#         datagen.fit(X_train)
#         validation_gen.fit(X_valid)
#         test_gen.fit(X_test)

#         # put model together
#         input_to_model = tf.keras.Input(X_train.shape[1:])
#         model = tf.keras.models.Model(
#             inputs=[input_to_model], outputs=[cnn(input_to_model)]
#         )
#         model_path = self.output_folder + "/model.keras"
#         weights_path = self.output_folder + "/model_weights.hdf5"

#         metrics_measures = [
#             tf.keras.metrics.TruePositives(name="tp"),
#             tf.keras.metrics.FalsePositives(name="fp"),
#             tf.keras.metrics.TrueNegatives(name="tn"),
#             tf.keras.metrics.FalseNegatives(name="fn"),
#             tf.keras.metrics.BinaryAccuracy(name="accuracy"),
#             tf.keras.metrics.Precision(name="precision"),
#             tf.keras.metrics.Recall(name="recall"),
#             tf.keras.metrics.AUC(name="auc"),
#             tf.keras.metrics.AUC(name="prc", curve="PR"),  # precision-recall curve
#         ]

#         lr_decayed_fn = tf.keras.optimizers.schedules.CosineDecayRestarts(
#             initial_learning_rate=0.001, first_decay_steps=300
#         )

#         opt_adam = tf.keras.optimizers.Adam(
#             learning_rate=lr_decayed_fn, epsilon=0.0000001, amsgrad=True
#         )
#         model.compile(
#             loss="binary_crossentropy", optimizer=opt_adam, metrics=metrics_measures
#         )

#         earlystop = tf.keras.callbacks.EarlyStopping(
#             monitor="val_accuracy",
#             min_delta=0.001,
#             patience=5,
#             verbose=1,
#             mode="max",
#             restore_best_weights=True,
#         )

#         checkpoint = tf.keras.callbacks.ModelCheckpoint(
#             model_path,
#             monitor="val_accuracy",
#             verbose=1,
#             save_best_only=True,
#             mode="max",
#         )
#         # callbacks_list = [checkpoint]
#         callbacks_list = [checkpoint, earlystop]

#         start = time.time()

#         history = model.fit(
#             datagen.flow(X_train, Y_train, batch_size=32),
#             epochs=100,
#             callbacks=callbacks_list,
#             validation_data=validation_gen.flow(X_valid, Y_valid, batch_size=32),
#         )

#         val_score = model.evaluate(
#             validation_gen.flow(X_valid, Y_valid, batch_size=32),
#             batch_size=32,
#             steps=len(Y_valid) // 32,
#         )
#         test_score = model.evaluate(
#             test_gen.flow(X_test, Y_test, batch_size=32),
#             batch_size=32,
#             steps=len(Y_test) // 32,
#         )

#         train_score = model.evaluate(
#             datagen.flow(X_train, Y_train, batch_size=32),
#             batch_size=32,
#             steps=len(Y_train) // 32,
#         )
#         self.model = model
#         print(
#             "Training and testing model took {} seconds".format(
#                 round(time.time() - start, 3)
#             )
#         )

#         df_history = pl.DataFrame(history.history)
#         self.history = df_history

#         if self.output_folder is not None:
#             model.save(self.output_folder + "/model.keras")

#     def predict(self, _iter=1):
#         """
#         Makes predictions on the test data using the trained CNN model.

#         This method loads test data, processes it, and applies the trained model to generate predictions.

#         Raises:
#             AssertionError: If the model has not been trained or loaded.
#         """
#

#         assert self.model is not None, "Please input the CNN trained model"

#         assert self.test_data is not None, "Please input training data"

#         # import data to predict
#         if isinstance(self.test_data, str):
#             assert (
#                 isinstance(self.test_data, pl.DataFrame)
#                 or "txt" in self.test_data
#                 or "csv" in self.test_data
#                 or self.test_data.endswith(".parquet")
#             ), "Please input a pl.DataFrame or save it as CSV or parquet"
#             try:
#                 df_test = pl.read_parquet(self.test_data)
#             except:
#                 df_test = pl.read_csv(self.test_data, separator=",")
#             if self.num_stats < 17:
#                 df_test = df_test.select(
#                     [col for col in df_test.columns if "flip" not in col]
#                 )

#             regions = df_test["iter"].to_numpy()
#             # Same folder custom fvs name based on input VCF.
#             self.output_prediction = (
#                 os.path.basename(self.test_data)
#                 .replace("fvs_", "")
#                 .replace(".parquet", "_predictions.txt")
#             )
#         else:
#             test_X, test_X_params, test_Y = self.test_data

#         # d_prediction = {}
#         # for m, df_m in df_test.group_by("model"):
#         #     test_X = []
#         #     for i in [
#         #         "dind",
#         #         "haf",
#         #         "hapdaf_o",
#         #         "isafe",
#         #         "high_freq",
#         #         "hapdaf_s",
#         #         "nsl",
#         #         "s_ratio",
#         #         "low_freq",
#         #         "ihs",
#         #         "h12",
#         #     ]:
#         #         if i == "ihs":
#         #             test_X.append(
#         #                 df_m.select(pl.col("^.*" + i + ".*$").exclude("^.*hapbin.*$"))
#         #             )
#         #         else:
#         #             test_X.append(
#         #                 df_m.select(pl.col("^.*" + i + ".*$").exclude("^.*flip.*$"))
#         #             )

#         #     test_X = (
#         #         pl.concat(test_X, how="horizontal")
#         #         .select(pl.exclude("^.*ihh.*$"))
#         #         .to_numpy()
#         #     )

#         #     test_X = test_X.reshape(
#         #         test_X.shape[0],
#         #         self.num_stats,
#         #         self.windows.size * self.center.size,
#         #         1,
#         #     )

#         # batch size, image width, image height,number of channels
#         if isinstance(self.model, str):
#             model = tf.keras.models.load_model(self.model)
#         else:
#             model = self.model

#         metrics_measures = [
#             tf.keras.metrics.TruePositives(name="tp"),
#             tf.keras.metrics.FalsePositives(name="fp"),
#             tf.keras.metrics.TrueNegatives(name="tn"),
#             tf.keras.metrics.FalseNegatives(name="fn"),
#             tf.keras.metrics.BinaryAccuracy(name="accuracy"),
#             tf.keras.metrics.Precision(name="precision"),
#             tf.keras.metrics.Recall(name="recall"),
#             tf.keras.metrics.AUC(name="auc"),
#             tf.keras.metrics.AUC(name="prc", curve="PR"),
#         ]

#         lr_decayed_fn = tf.keras.optimizers.schedules.CosineDecayRestarts(
#             initial_learning_rate=0.001, first_decay_steps=300
#         )
#         opt_adam = tf.keras.optimizers.Adam(
#             learning_rate=lr_decayed_fn, epsilon=0.0000001, amsgrad=True
#         )
#         model.compile(
#             loss="binary_crossentropy", optimizer=opt_adam, metrics=metrics_measures
#         )

#         validation_gen = tf.keras.preprocessing.image.ImageDataGenerator(
#             featurewise_center=True,
#             featurewise_std_normalization=True,
#             horizontal_flip=False,
#         )

#         validation_gen.fit(test_X)

#         # make predictions
#         preds = model.predict(validation_gen.standardize(test_X))
#         predictions = np.argmax(preds, axis=1)
#         prediction_dict = {0: "sweep", 1: "neutral"}
#         predictions_class = np.vectorize(prediction_dict.get)(predictions)

#         df_prediction = pl.concat(
#             [
#                 test_X_params.select(pl.nth([5, 0, 1, 2, 3])),
#                 # df_m.select(pl.nth([0])),
#                 pl.DataFrame(
#                     np.column_stack([predictions_class, preds]),
#                     schema=["predicted_model", "prob_sweep", "prob_neutral"],
#                 ),
#             ],
#             how="horizontal",
#         )
#         # d_prediction[m[0]] = df_prediction

#         # df_prediction = pl.concat(d_prediction.values(), how="vertical")
#         # df_prediction.iloc[:, -2:] = df_prediction.iloc[:, -2:].astype(float)

#         if isinstance(self.test_data, str):
#             df_prediction = df_prediction.with_columns(pl.Series("region", regions))
#             chr_start_end = np.array(
#                 [item.replace(":", "-").split("-") for item in regions]
#             )

#             df_prediction = df_prediction.with_columns(
#                 pl.Series("chr", chr_start_end[:, 0]),
#                 pl.Series("start", chr_start_end[:, 1], dtype=pl.Int64),
#                 pl.Series("end", chr_start_end[:, 2], dtype=pl.Int64),
#             )
#             df_prediction = (
#                 df_prediction.select(pl.exclude("region"))
#                 .sort("start")
#                 .select(df_prediction.columns[-3:] + df_prediction.columns[:-4])
#             )

#         self.prediction = df_prediction

#         if self.output_folder is not None:
#             df_prediction.write_csv(
#                 # f"{self.output_folder}/predictions.txt"
#                 f"{self.output_folder}/predictions.txt"
#             )

#         return df_prediction

#     def roc_curve(self):
#         """
#         Generates and plots ROC curves along with a history plot of model metrics.

#         Returns:
#             tuple: A tuple containing:
#                 - plot_roc (Figure): The ROC curve plot.
#                 - plot_history (Figure): The history plot of model metrics (loss, validation loss, accuracy, validation accuracy).

#         Example:
#             roc_plot, history_plot = model.roc_curves()
#             plt.show(roc_plot)
#             plt.show(history_plot)
#         """
#         import matplotlib.pyplot as plt

#         pred_data = self.prediction

#         # Create confusion dataframe
#         confusion_data = pred_data.group_by(["model", "predicted_model"]).agg(
#             pl.len().alias("n")
#         )

#         expected_combinations = pl.DataFrame(
#             {
#                 "model": ["sweep", "sweep", "neutral", "neutral"],
#                 "predicted_model": ["sweep", "neutral", "neutral", "sweep"],
#             }
#         )

#         confusion_data = expected_combinations.join(
#             confusion_data, on=["model", "predicted_model"], how="left"
#         ).fill_null(
#             0
#         )  # Fill missing values with 0
#         # Adding the "true_false" column
#         confusion_data = confusion_data.with_columns(
#             pl.when(
#                 (pl.col("model") == pl.col("predicted_model"))
#                 & (pl.col("model") == "neutral")
#             )
#             .then(pl.lit("true_negative"))  # Explicit literal for Polars
#             .when(
#                 (pl.col("model") == pl.col("predicted_model"))
#                 & (pl.col("model") == "sweep")
#             )
#             .then(pl.lit("true_positive"))  # Explicit literal for Polars
#             .when(
#                 (pl.col("model") != pl.col("predicted_model"))
#                 & (pl.col("model") == "neutral")
#             )
#             .then(pl.lit("false_positive"))  # Explicit literal for Polars
#             .otherwise(pl.lit("false_negative"))  # Explicit literal for Polars
#             .alias("true_false")
#         )

#         confusion_pivot = confusion_data.pivot(
#             values="n", index=None, on="true_false", aggregate_function="sum"
#         ).fill_null(0)

#         # Copying the pivoted data (optional as Polars is immutable)
#         rate_data = confusion_pivot.select(
#             ["false_negative", "false_positive", "true_negative", "true_positive"]
#         ).sum()

#         # Compute the required row sums for normalization
#         required_cols = [
#             "false_negative",
#             "false_positive",
#             "true_negative",
#             "true_positive",
#         ]
#         for col in required_cols:
#             if col not in rate_data.columns:
#                 rate_data[col] = 0

#         # Calculate row sums for normalization
#         rate_data = rate_data.with_columns(
#             (pl.col("false_negative") + pl.col("true_positive")).alias("sum_fn_tp")
#         )
#         rate_data = rate_data.with_columns(
#             (pl.col("false_positive") + pl.col("true_negative")).alias("sum_fp_tn")
#         )

#         # Compute normalized rates
#         rate_data = rate_data.with_columns(
#             (pl.col("false_negative") / pl.col("sum_fn_tp")).alias("false_negative"),
#             (pl.col("false_positive") / pl.col("sum_fp_tn")).alias("false_positive"),
#             (pl.col("true_negative") / pl.col("sum_fp_tn")).alias("true_negative"),
#             (pl.col("true_positive") / pl.col("sum_fn_tp")).alias("true_positive"),
#         )

#         # Replace NaN values with 0
#         rate_data = rate_data.with_columns(
#             [
#                 pl.col("false_negative").fill_null(0).alias("false_negative"),
#                 pl.col("false_positive").fill_null(0).alias("false_positive"),
#                 pl.col("true_negative").fill_null(0).alias("true_negative"),
#                 pl.col("true_positive").fill_null(0).alias("true_positive"),
#             ]
#         )

#         # Calculate accuracy and precision
#         rate_data = rate_data.with_columns(
#             [
#                 (
#                     (pl.col("true_positive") + pl.col("true_negative"))
#                     / (
#                         pl.col("true_positive")
#                         + pl.col("true_negative")
#                         + pl.col("false_positive")
#                         + pl.col("false_negative")
#                     )
#                 ).alias("accuracy"),
#                 (
#                     pl.col("true_positive")
#                     / (pl.col("true_positive") + pl.col("false_positive"))
#                 )
#                 .fill_null(0)
#                 .alias("precision"),
#             ]
#         )

#         # Compute ROC AUC and prepare roc_data. Set 'sweep' as the positive class
#         pred_rate_auc_data = pred_data.clone().with_columns(
#             pl.col("model").cast(pl.Categorical).alias("model")
#         )

#         # Calculate ROC AUC
#         roc_auc_value = roc_auc_score(
#             (pred_rate_auc_data["model"] == "sweep").cast(int),
#             pred_rate_auc_data["prob_sweep"].cast(float),
#         )

#         # Create roc_data DataFrame
#         roc_data = pl.DataFrame({"AUC": [roc_auc_value]})

#         rate_roc_data = pl.concat([pl.DataFrame(rate_data), roc_data], how="horizontal")

#         first_row_values = rate_roc_data.row(0)

#         pred_rate_auc_data = pred_rate_auc_data.with_columns(
#             [
#                 pl.lit(value).alias(col)
#                 for col, value in zip(rate_roc_data.columns, first_row_values)
#             ]
#         )

#         # Compute ROC curve using sklearn
#         fpr, tpr, thresholds = roc_curve(
#             (pred_rate_auc_data["model"] == "sweep").cast(int),
#             pred_rate_auc_data["prob_sweep"].cast(float),
#         )

#         roc_df = pl.DataFrame({"false_positive_rate": fpr, "sensitivity": tpr})

#         fig, ax = plt.subplots(figsize=(10, 6))
#         ax.plot(
#             roc_df["false_positive_rate"],
#             roc_df["sensitivity"],
#             color="orange",
#             linewidth=2,
#             label="ROC Curve",
#         )
#         ax.plot(
#             [0, 1], [0, 1], color="grey", linestyle="--"
#         )  # Diagonal line for reference
#         ax.set_xlabel("false positive rate")
#         ax.set_ylabel("power")
#         ax.set_title("ROC Curve")
#         ax.axis("equal")  # Equivalent to coord_equal in ggplot
#         ax.grid(True, which="both", linestyle="--", linewidth=0.5)
#         ax.legend()
#         fig.tight_layout()
#         plot_roc = fig

#         ## History
#         # Load and preprocess the data
#         history_data = self.history
#         h = history_data.select(
#             ["loss", "val_loss", "accuracy", "val_accuracy"]
#         ).clone()

#         h = h.with_columns((pl.arange(0, h.height) + 1).alias("epoch"))

#         h_melted = h.unpivot(
#             index=["epoch"],
#             on=["loss", "val_loss", "accuracy", "val_accuracy"],
#             variable_name="metric_name",
#             value_name="metric_val",
#         )

#         line_styles = {
#             "loss": "-",
#             "val_loss": "--",
#             "accuracy": "-",
#             "val_accuracy": "--",
#         }
#         colors = {
#             "loss": "orange",
#             "val_loss": "orange",
#             "accuracy": "blue",
#             "val_accuracy": "blue",
#         }

#         fig, ax = plt.subplots(figsize=(10, 6))

#         for group_name, group_df in h_melted.group_by("metric_name"):
#             ax.plot(
#                 group_df["epoch"].to_numpy(),
#                 group_df["metric_val"].to_numpy(),
#                 label=group_name[0],
#                 linestyle=line_styles[group_name[0]],
#                 color=colors[group_name[0]],
#                 linewidth=2,
#             )
#         ax.set_title("History")
#         ax.set_xlabel("Epoch")
#         ax.set_ylabel("Value")
#         ax.tick_params(axis="both", labelsize=10)
#         ax.grid(True)
#         ax.legend(title="", loc="upper right")

#         plot_history = fig

#         if self.output_folder is not None:
#             plot_roc.savefig(self.output_folder + "/roc_curve.svg")
#             plot_history.savefig(self.output_folder + "/train_history.svg")
#         return plot_roc, plot_history
