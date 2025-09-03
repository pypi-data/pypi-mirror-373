"""API Module"""

class api:

    def __init__(self, url, status_url, headers, verbose=False):
        import requests
        self.url = url
        self.status_url = status_url
        self.headers = headers or {}
        self.verbose = verbose
        self.types = None
        self.fields = {}
        self.session = requests.Session()
        if self.headers:
            self.session.headers.update(self.headers)

    def login(self, email, password):
        import time
        fields = self.getTypeFields("UserCredentials")
        fields = "\n".join(fields)
        response = self.session.post(
            url = self.url,
            json = {
                "operationName": "signIn",
                "variables": {
                    "email": email,
                    "password": password
                },
                "query": f"""mutation
                    signIn($email: String!, $password: String!) {{
                        signIn(email: $email, password: $password) {{
                            {fields}
                        }}
                    }}"""})
        if 'errors' in response.json(): return False
        data = self.errorhandler(response, "signIn")
        data['expiresAt'] = time.time() + data['expires']
        return data


    def close(self):
        self.session.close()


    def getSystemNotifications(self):
        if self.status_url is None: return None
        response = self.session.post(
            url = self.status_url,
            json = {
                "operationName": "getSystemNotifications",
                "variables": {},
                "query": """query
                    getSystemNotifications {
                        getSystemNotifications {
                            message
                            notificationId
                        }
                    }"""})
        if 'errors' in response.json(): return False
        return self.errorhandler(response, "getSystemNotifications")


    def getSystemStatus(self, serviceId=None):
        if self.status_url is None: return None
        response = self.session.post(
            url = self.status_url,
            json = {
                "operationName": "getSystemStatus",
                "variables": {
                    "serviceId": serviceId
                },
                "query": """query
                    getSystemStatus($serviceId: String) {
                        getSystemStatus(serviceId: $serviceId) {
                            serviceId
                            serviceName
                            description
                            status
                            type
                            updatedAt
                            createdAt
                        }
                    }"""})
        if 'errors' in response.json(): return False
        return self.errorhandler(response, "getSystemStatus")


    def getSDKCompatibility(self):
        import anatools
        import platform
        os = str(platform.system_alias(platform.system(), platform.release(), platform.version()))
        python = str(platform.python_version())
        anatools = str(anatools.__version__)
        response = self.session.post(
            url = self.url,
            json = {
                "operationName": "getSDKCompatibility",
                "variables": {
                    "os": os,
                    "python": python,
                    "anatools": anatools
                },
                "query": """query
                    getSDKCompatibility($os: String!, $python: String!, $anatools: String!) {
                        getSDKCompatibility(os: $os, python: $python, anatools: $anatools) {
                            version
                            message
                        }
                    }"""
            })
        if 'errors' in response.json(): return False
        return self.errorhandler(response, "getSDKCompatibility")


    def errorhandler(self, response, call):
        responsedata = response.json()
        if self.verbose == 'debug': print(responsedata)
        try:
            if 'data' in responsedata and call in responsedata['data']: return responsedata['data'][call]
            elif 'errors' in responsedata: raise Exception(responsedata['errors'][-1]['message'])
            else: raise Exception()
        except Exception as e:
            raise Exception(f'There was an issue with the {call} API call: {e}')


    from .organizations import getOrganizations, editOrganization
    from .channels      import getChannels, getChannelDeployment, getChannelSchema, createChannel, deleteChannel, editChannel, deployChannel, getChannelDocumentation, uploadChannelDocumentation, getNodeDocumentation
    from .volumes       import getVolumes, getVolumes, createVolume, deleteVolume, editVolume, editVolumeData, getVolumeData, uploadVolumeData, uploadVolumeDataFinalizer, deleteVolumeData, mountVolumes, addWorkspaceVolumes, removeWorkspaceVolumes
    from .members       import getMembers, addMember, removeMember, editMember, getInvitations
    from .workspaces    import getWorkspaces, createWorkspace, deleteWorkspace, editWorkspace, mountWorkspaces
    from .graphs        import getGraphs, uploadGraph, deleteGraph, editGraph, downloadGraph, getDefaultGraph, setDefaultGraph
    from .datasets      import getDatasets, getDatasetJobs, createDataset, deleteDataset, editDataset, downloadDataset, cancelDataset, datasetUpload, datasetUploadFinalizer, getDatasetRuns, getDatasetLog, getDatasetFiles, createMixedDataset
    from .analytics     import getAnalytics, getAnalyticsTypes, createAnalytics, deleteAnalytics, editAnalytics
    from .annotations   import getAnnotations, getAnnotationFormats, getAnnotationMaps, createAnnotation, downloadAnnotation, deleteAnnotation, editAnnotation, getAnnotationMaps, createAnnotationMap, editAnnotationMap, deleteAnnotationMap, downloadAnnotationMap
    from .graphs        import getGraphs, uploadGraph, deleteGraph, editGraph, downloadGraph, getDefaultGraph
    from .datasets      import getDatasets, getDatasetJobs, createDataset, deleteDataset, editDataset, downloadDataset, cancelDataset, datasetUpload, datasetUploadFinalizer, getDatasetRuns, getDatasetLog, getDatasetFiles, createMixedDataset
    from .analytics     import getAnalytics, getAnalyticsTypes, createAnalytics, deleteAnalytics
    from .annotations   import getAnnotations, getAnnotationFormats, getAnnotationMaps, createAnnotation, downloadAnnotation, deleteAnnotation, createAnnotationMap, editAnnotationMap, deleteAnnotationMap, downloadAnnotationMap
    from .gan           import getGANModels, getGANDatasets, createGANDataset, deleteGANDataset, uploadGANModel, uploadGANModelFinalizer, deleteGANModel, editGANModel, downloadGANModel
    from .umap          import getUMAPs, createUMAP, deleteUMAP
    from .api_keys      import getAPIKeys, createAPIKey, deleteAPIKey, getAPIKeyContext, getCurrentUserContext
    from .llm           import getLLMResponse, createLLMPrompt, deleteLLMPrompt, getLLMBaseChannels, getLLMChannelNodeTypes
    from .editor        import createRemoteDevelopment, deleteRemoteDevelopment, listRemoteDevelopment, startRemoteDevelopment, stopRemoteDevelopment, inviteRemoteDevelopment, createSSHKey, deleteSSHKey, getSSHKeys, getEditors, createEditor, deleteEditor, editEditor, startEditor, stopEditor
    from .ml            import getMLArchitectures, getMLModels, createMLModel, deleteMLModel, editMLModel, downloadMLModel, uploadMLModel, uploadMLModelFinalizer, getMLInferences, getMLInferenceMetrics, createMLInference, deleteMLInference, editMLInference, downloadMLInference
    from .inpaint       import getInpaints, getInpaintLog, createInpaint, deleteInpaint
    from .preview       import getPreview, createPreview
    from .image         import getImageAnnotation, getImageMask, getImageMetadata
    from .introspection import getTypes, getTypeFields
    from .services      import getServiceTypes, getServices, createService, editService, deleteService, deployService, getServiceDeployment, addWorkspaceServices, removeWorkspaceServices, getServiceJobs, createServiceJob, deleteServiceJob, getWorkspaceServiceCredentials, getInstanceTypes
    from .rules         import getPlatformRules,getOrganizationRules, getWorkspaceRules, getServiceRules, getUserRules, editOrganizationRules, editWorkspaceRules, editServiceRules, editUserRules