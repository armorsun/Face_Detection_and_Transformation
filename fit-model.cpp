/*
 * eos - A 3D Morphable Model fitting library written in modern C++11/14.
 *
 * File: examples/fit-model.cpp
 *
 * Copyright 2016 Patrik Huber
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "eos/core/Landmark.hpp"
#include "eos/core/LandmarkMapper.hpp"
#include "eos/morphablemodel/MorphableModel.hpp"
#include "eos/morphablemodel/Blendshape.hpp"
#include "eos/fitting/fitting.hpp"
#include "eos/render/utils.hpp"
#include "eos/render/texture_extraction.hpp"
#include "eos/render/render.hpp"

#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"

#include "boost/program_options.hpp"
#include "boost/filesystem.hpp"

#include <vector>
#include <iostream>
#include <fstream>

using namespace eos;
namespace po = boost::program_options;
namespace fs = boost::filesystem;
using eos::core::Landmark;
using eos::core::LandmarkCollection;
using cv::Mat;
using cv::Vec2f;
using cv::Vec3f;
using cv::Vec4f;
using std::cout;
using std::endl;
using std::vector;
using std::string;

void read_expression_file(std::string filename, std::vector<float> &blendshape_coeffs) {
	std::ifstream file(filename);
	float coeff;
	string line;
	while (getline(file, line)) {
		std::stringstream lineStream(line);
		lineStream >> coeff;
		blendshape_coeffs.push_back(coeff);
	}
}

/**
 * Reads an ibug .pts landmark file and returns an ordered vector with
 * the 68 2D landmark coordinates.
 *
 * @param[in] filename Path to a .pts file.
 * @return An ordered vector with the 68 ibug landmarks.
 */
LandmarkCollection<cv::Vec2f> read_pts_landmarks(std::string filename)
{
	using std::getline;
	using cv::Vec2f;
	using std::string;
	LandmarkCollection<Vec2f> landmarks;
	landmarks.reserve(68);

	std::ifstream file(filename);
	if (!file.is_open()) {
		throw std::runtime_error(string("Could not open landmark file: " + filename));
	}

	string line;
	// Skip the first 3 lines, they're header lines:
	getline(file, line); // 'version: 1'
	getline(file, line); // 'n_points : 68'
	getline(file, line); // '{'

	int ibugId = 1;
	while (getline(file, line))
	{
		if (line == "}") { // end of the file
			break;
		}
		std::stringstream lineStream(line);

		Landmark<Vec2f> landmark;
		landmark.name = std::to_string(ibugId);
		if (!(lineStream >> landmark.coordinates[0] >> landmark.coordinates[1])) {
			throw std::runtime_error(string("Landmark format error while parsing the line: " + line));
		}
		// From the iBug website:
		// "Please note that the re-annotated data for this challenge are saved in the Matlab convention of 1 being
		// the first index, i.e. the coordinates of the top left pixel in an image are x=1, y=1."
		// ==> So we shift every point by 1:
		landmark.coordinates[0] -= 1.0f;
		landmark.coordinates[1] -= 1.0f;
		landmarks.emplace_back(landmark);
		++ibugId;
	}
	return landmarks;
};

/**
 * Draws the given mesh as wireframe into the image.
 *
 * It does backface culling, i.e. draws only vertices in CCW order.
 *
 * @param[in] image An image to draw into.
 * @param[in] mesh The mesh to draw.
 * @param[in] modelview Model-view matrix to draw the mesh.
 * @param[in] projection Projection matrix to draw the mesh.
 * @param[in] viewport Viewport to draw the mesh.
 * @param[in] colour Colour of the mesh to be drawn.
 */
void draw_wireframe(cv::Mat image, const core::Mesh& mesh, glm::mat4x4 modelview, glm::mat4x4 projection, glm::vec4 viewport, cv::Scalar colour = cv::Scalar(0, 255, 0, 255))
{
	for (const auto& triangle : mesh.tvi)
	{
		const auto p1 = glm::project({ mesh.vertices[triangle[0]][0], mesh.vertices[triangle[0]][1], mesh.vertices[triangle[0]][2] }, modelview, projection, viewport);
		const auto p2 = glm::project({ mesh.vertices[triangle[1]][0], mesh.vertices[triangle[1]][1], mesh.vertices[triangle[1]][2] }, modelview, projection, viewport);
		const auto p3 = glm::project({ mesh.vertices[triangle[2]][0], mesh.vertices[triangle[2]][1], mesh.vertices[triangle[2]][2] }, modelview, projection, viewport);
		if (render::detail::are_vertices_ccw_in_screen_space(glm::vec2(p1), glm::vec2(p2), glm::vec2(p3)))
		{
			cv::line(image, cv::Point(p1.x, p1.y), cv::Point(p2.x, p2.y), colour);
			cv::line(image, cv::Point(p2.x, p2.y), cv::Point(p3.x, p3.y), colour);
			cv::line(image, cv::Point(p3.x, p3.y), cv::Point(p1.x, p1.y), colour);
		}
	}
};

/**
 * This app demonstrates estimation of the camera and fitting of the shape
 * model of a 3D Morphable Model from an ibug LFPW image with its landmarks.
 * In addition to fit-model-simple, this example uses blendshapes, contour-
 * fitting, and can iterate the fitting.
 *
 * 68 ibug landmarks are loaded from the .pts file and converted
 * to vertex indices using the LandmarkMapper.
 */
int main(int argc, char *argv[])
{
	fs::path modelfile, isomapfile, imagefile, landmarksfile, mappingsfile, contourfile, edgetopologyfile, blendshapesfile, outputfile, expressionfile;
	try {
		po::options_description desc("Allowed options");
		desc.add_options()
			("help,h",
				"display the help message")
			("model,m", po::value<fs::path>(&modelfile)->required()->default_value("../share/sfm_shape_3448.bin"),
				"a Morphable Model stored as cereal BinaryArchive")
			("image,i", po::value<fs::path>(&imagefile)->required()->default_value("data/image_0010.png"),
				"an input image")
			("landmarks,l", po::value<fs::path>(&landmarksfile)->required()->default_value("data/image_0010.pts"),
				"2D landmarks for the image, in ibug .pts format")
			("mapping,p", po::value<fs::path>(&mappingsfile)->required()->default_value("../share/ibug_to_sfm.txt"),
				"landmark identifier to model vertex number mapping")
			("model-contour,c", po::value<fs::path>(&contourfile)->required()->default_value("../share/model_contours.json"),
				"file with model contour indices")
			("edge-topology,e", po::value<fs::path>(&edgetopologyfile)->required()->default_value("../share/sfm_3448_edge_topology.json"),
				"file with model's precomputed edge topology")
			("blendshapes,b", po::value<fs::path>(&blendshapesfile)->required()->default_value("../share/expression_blendshapes_3448.bin"),
				"file with blendshapes")
			("output,o", po::value<fs::path>(&outputfile)->required()->default_value("out"),
				"basename for the output rendering and obj files")
			("expression,x", po::value<fs::path>(&expressionfile)->required()->default_value("data/epression.txt"),
				"6 expression values for blendshape coefficients")
			;
		po::variables_map vm;
		po::store(po::command_line_parser(argc, argv).options(desc).run(), vm);
		if (vm.count("help")) {
			cout << "Usage: fit-model [options]" << endl;
			cout << desc;
			return EXIT_SUCCESS;
		}
		po::notify(vm);
	}
	catch (const po::error& e) {
		cout << "Error while parsing command-line arguments: " << e.what() << endl;
		cout << "Use --help to display a list of options." << endl;
		return EXIT_FAILURE;
	}

	// Load the image, landmarks, LandmarkMapper and the Morphable Model:
	Mat image = cv::imread(imagefile.string());
	LandmarkCollection<cv::Vec2f> landmarks;
	try {
		landmarks = read_pts_landmarks(landmarksfile.string());
	}
	catch (const std::runtime_error& e) {
		cout << "Error reading the landmarks: " << e.what() << endl;
		return EXIT_FAILURE;
	}
	morphablemodel::MorphableModel morphable_model;
	try {
		morphable_model = morphablemodel::load_model(modelfile.string());
	}
	catch (const std::runtime_error& e) {
		cout << "Error loading the Morphable Model: " << e.what() << endl;
		return EXIT_FAILURE;
	}
	// The landmark mapper is used to map ibug landmark identifiers to vertex ids:
	core::LandmarkMapper landmark_mapper = mappingsfile.empty() ? core::LandmarkMapper() : core::LandmarkMapper(mappingsfile);

	// The expression blendshapes:
	vector<morphablemodel::Blendshape> blendshapes = morphablemodel::load_blendshapes(blendshapesfile.string());

	// These two are used to fit the front-facing contour to the ibug contour landmarks:
	fitting::ModelContour model_contour = contourfile.empty() ? fitting::ModelContour() : fitting::ModelContour::load(contourfile.string());
	fitting::ContourLandmarks ibug_contour = fitting::ContourLandmarks::load(mappingsfile.string());

	// The edge topology is used to speed up computation of the occluding face contour fitting:
	morphablemodel::EdgeTopology edge_topology = morphablemodel::load_edge_topology(edgetopologyfile.string());
	
	std::vector<float> adjust_blendshape_coeffs;
	read_expression_file(expressionfile.string(), adjust_blendshape_coeffs);
	for (size_t i = 0; i < adjust_blendshape_coeffs.size(); ++i)
		printf("%f ", adjust_blendshape_coeffs[i]);
	printf("\n");

	// Draw the loaded landmarks:
	Mat outimg = image.clone();
	for (auto&& lm : landmarks) {
		cv::rectangle(outimg, cv::Point2f(lm.coordinates[0] - 2.0f, lm.coordinates[1] - 2.0f), cv::Point2f(lm.coordinates[0] + 2.0f, lm.coordinates[1] + 2.0f), { 255, 0, 0 });
	}

	// Fit the model, get back a mesh and the pose:
	core::Mesh mesh;
	fitting::RenderingParameters rendering_params;
	// std::tie(mesh, rendering_params) = fitting::fit_shape_and_pose(morphable_model, blendshapes, landmarks, landmark_mapper, image.cols, image.rows, edge_topology, ibug_contour, model_contour, 50, boost::none, 30.0f);
	std::vector<float> shape_coeffs;
	std::vector<float> blendshape_coeffs;
	std::vector<cv::Vec2f> fitted_image_points;
	std::tie(mesh, rendering_params) = fitting::fit_shape_and_pose(morphable_model, blendshapes, landmarks, landmark_mapper, image.cols, image.rows, edge_topology, ibug_contour, model_contour, 50, boost::none, 30.0f, boost::none, shape_coeffs, blendshape_coeffs, fitted_image_points);
	for (size_t i = 0; i < blendshape_coeffs.size(); ++i)
		printf("%f ", blendshape_coeffs[i]);
	printf("\n");

	// Extract the texture from the image using given mesh and camera parameters:
	Mat affine_from_ortho = fitting::get_3x4_affine_camera_matrix(rendering_params, image.cols, image.rows);
	Mat isomap = render::extract_texture(mesh, affine_from_ortho, image);
	// And save the isomap:
	outputfile.replace_extension(".isomap.png");
	cv::imwrite(outputfile.string(), isomap);

	// Draw the fitted mesh as wireframe, and save the image:
	draw_wireframe(outimg, mesh, rendering_params.get_modelview(), rendering_params.get_projection(), fitting::get_opencv_viewport(image.cols, image.rows));
	outputfile += fs::path(".png");
	cv::imwrite(outputfile.string(), outimg);

	Mat color_buf, depth_buf;
	std::tie(color_buf, depth_buf) = render::render(mesh, rendering_params.get_modelview(), rendering_params.get_projection(), image.cols, image.rows, render::create_mipmapped_texture(isomap), true, false, false);
	outputfile.replace_extension("render.png");
	cv::imwrite(outputfile.string(), color_buf);


	// float coeffs[] = {0.0, 0.0, 0.0, 1.0, 0.0, 0.0};
	// std::vector<float> adjust_blendshape_coeffs(coeffs, coeffs + sizeof(coeffs) / sizeof(float));
	Eigen::VectorXf shape = morphable_model.get_shape_model().draw_sample(shape_coeffs) + morphablemodel::to_matrix(blendshapes) * Eigen::Map<const Eigen::VectorXf>(adjust_blendshape_coeffs.data(), adjust_blendshape_coeffs.size());
	mesh = morphablemodel::sample_to_mesh(shape, morphable_model.get_color_model().get_mean(), morphable_model.get_shape_model().get_triangle_list(), morphable_model.get_color_model().get_triangle_list(), morphable_model.get_texture_coordinates());

	// The 2D and 3D point correspondences used for the fitting:
	vector<Vec4f> model_points; // the points in the 3D shape model
	vector<int> vertex_indices; // their vertex indices
	vector<Vec2f> image_points; // the corresponding 2D landmark points

	// Sub-select all the landmarks which we have a mapping for (i.e. that are defined in the 3DMM),
	// and get the corresponding model points (mean if given no initial coeffs, from the computed shape otherwise):
	for (int i = 0; i < landmarks.size(); ++i) {
		auto converted_name = landmark_mapper.convert(landmarks[i].name);
		if (!converted_name) { // no mapping defined for the current landmark
			continue;
		}
		int vertex_idx = std::stoi(converted_name.get());
		Vec4f vertex(mesh.vertices[vertex_idx].x, mesh.vertices[vertex_idx].y, mesh.vertices[vertex_idx].z, mesh.vertices[vertex_idx].w);
		model_points.emplace_back(vertex);
		vertex_indices.emplace_back(vertex_idx);
		image_points.emplace_back(landmarks[i].coordinates);
	}

	// Need to do an initial pose fit to do the contour fitting inside the loop.
	// We'll do an expression fit too, since face shapes vary quite a lot, depending on expressions.
	fitting::ScaledOrthoProjectionParameters pose;
	pose = fitting::estimate_orthographic_projection_linear(image_points, model_points, true, image.rows);
	rendering_params = fitting::RenderingParameters(pose, image.cols, image.rows);

	// The 3D head pose can be recovered as follows:
	float yaw_angle = glm::degrees(glm::yaw(rendering_params.get_rotation()));
	// and similarly for pitch and roll.

	// Save the mesh as textured obj:
	outputfile.replace_extension("emo.obj");
	core::write_textured_obj(mesh, outputfile.string());

	std::tie(color_buf, depth_buf) = render::render(mesh, rendering_params.get_modelview(), rendering_params.get_projection(), image.cols, image.rows, render::create_mipmapped_texture(isomap), true, false, false);
	outputfile.replace_extension(".png");
	cv::imwrite(outputfile.string(), color_buf);

	cout << "Finished fitting and wrote result mesh and isomap to files with basename " << outputfile.stem().stem() << "." << endl;

	return EXIT_SUCCESS;
}
